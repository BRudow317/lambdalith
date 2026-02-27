"""DynamoDB table accessors.

Single boto3 resource cached at module level for Lambda warm-start reuse.
All table names come from app.config so there is one place to change them.
"""

import boto3

from . import config

_dynamodb = None


def _get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb")
    return _dynamodb

def users_table():
    """Return the Users table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for the Users table.
    """
    return _get_dynamodb().Table(config.USERS_TABLE)


def resume_table():
    """Return the Resume table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for the Resume table.
    """
    return _get_dynamodb().Table(config.RESUME_TABLE)


def blacklist_table():
    """Return the TokenBlacklist table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for revoked JWTs.
    """
    return _get_dynamodb().Table(config.BLACKLIST_TABLE)


def password_reset_table():
    """Return the PasswordResetTokens table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for reset tokens.
    """
    return _get_dynamodb().Table(config.PASSWORD_RESET_TABLE)


def login_attempts_table():
    """Return the LoginAttempts table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for rate-limiting data.
    """
    return _get_dynamodb().Table(config.LOGIN_ATTEMPTS_TABLE)
