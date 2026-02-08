"""FastAPI dependencies for auth and tenant resolution."""

import jwt
from fastapi import Header, HTTPException

from ..config import API_KEYS, get_jwt_secret
from ..db import blacklist_table


def resolve_tenant(api_key: str) -> dict:
    """Validate an API key value and return the tenant context.

    Args:
        api_key: The API key value to resolve.

    Returns:
        A dict with ``client_id`` and ``site_id`` for the matched tenant.

    Raises:
        HTTPException: 403 if the key is not in the allowed set.
    """
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return API_KEYS[api_key]


def get_tenant(x_api_key: str = Header()) -> dict:
    """Validate the API key header and return the tenant context.

    Args:
        x_api_key: Value of the ``x-api-key`` request header.

    Returns:
        A dict with ``client_id`` and ``site_id`` for the matched tenant.

    Raises:
        HTTPException: 403 if the key is not in the allowed set.
    """
    return resolve_tenant(x_api_key)


def get_current_user(authorization: str = Header()) -> dict:
    """Extract and verify the JWT from the Authorization header.

    Decodes the token, checks the blacklist, and returns the full
    decoded payload for downstream route functions.

    Args:
        authorization: Raw ``Authorization`` header value (``Bearer <token>``).

    Returns:
        The decoded JWT payload dict (includes ``user_id``, ``email``,
        ``client_id``, ``site_id``, ``jti``, ``exp``, ``iat``).

    Raises:
        HTTPException: 401 if the header is missing, the token is expired,
            invalid, or has been revoked via the blacklist.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    if jti:
        table = blacklist_table()
        result = table.get_item(Key={"token_jti": jti})
        if "Item" in result:
            raise HTTPException(status_code=401, detail="Token revoked")

    return payload
