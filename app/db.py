"""DynamoDB table accessors.

Single boto3 resource cached at module level for Lambda warm-start reuse.
All table names come from app.config so there is one place to change them.
"""

import boto3

from . import config

_dynamodb = boto3.resource("dynamodb")


def users_table():
    """Return the Users table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for the Users table.
    """
    return _dynamodb.Table(config.USERS_TABLE)


def blacklist_table():
    """Return the TokenBlacklist table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for revoked JWTs.
    """
    return _dynamodb.Table(config.BLACKLIST_TABLE)


def password_reset_table():
    """Return the PasswordResetTokens table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for reset tokens.
    """
    return _dynamodb.Table(config.PASSWORD_RESET_TABLE)


def login_attempts_table():
    """Return the LoginAttempts table resource.

    Returns:
        A ``boto3.resources.factory.dynamodb.Table`` for rate-limiting data.
    """
    return _dynamodb.Table(config.LOGIN_ATTEMPTS_TABLE)
