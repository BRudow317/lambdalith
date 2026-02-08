"""Runtime configuration and secrets management."""

import json
import os

import boto3

USERS_TABLE = os.environ.get("USERS_TABLE", "Users")
BLACKLIST_TABLE = os.environ.get("BLACKLIST_TABLE", "TokenBlacklist")
PASSWORD_RESET_TABLE = os.environ.get("PASSWORD_RESET_TABLE", "PasswordResetTokens")
LOGIN_ATTEMPTS_TABLE = os.environ.get("LOGIN_ATTEMPTS_TABLE", "LoginAttempts")

JWT_SECRET_NAME = os.environ.get("JWT_SECRET_NAME", "")
JWT_EXPIRY_HOURS = 24
REFRESH_THRESHOLD_HOURS = 2

API_KEYS = {
    "site_a_key_abc123": {"client_id": "ClientCustomerC", "site_id": "SiteA"},
    "site_b_key_xyz789": {"client_id": "ClientCustomerA", "site_id": "SiteB"},
}

_jwt_secret_cache = None


def get_jwt_secret() -> str:
    """Fetch the JWT signing secret, caching after first call.

    Uses Secrets Manager when ``JWT_SECRET_NAME`` is set (deployed
    environment).  Falls back to the ``JWT_SECRET`` env var for local
    development.  The result is cached in ``_jwt_secret_cache`` so
    Secrets Manager is only called once per Lambda cold start.

    Returns:
        The plaintext JWT signing secret.

    Raises:
        RuntimeError: If neither ``JWT_SECRET_NAME`` nor ``JWT_SECRET``
            is configured.
    """
    global _jwt_secret_cache
    if _jwt_secret_cache is not None:
        return _jwt_secret_cache

    if not JWT_SECRET_NAME:
        secret = os.environ.get("JWT_SECRET")
        if not secret:
            raise RuntimeError("Neither JWT_SECRET_NAME nor JWT_SECRET is configured")
        _jwt_secret_cache = secret
        return _jwt_secret_cache

    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=JWT_SECRET_NAME)
    secret_dict = json.loads(response["SecretString"])
    _jwt_secret_cache = secret_dict["jwt_secret"]
    return _jwt_secret_cache
