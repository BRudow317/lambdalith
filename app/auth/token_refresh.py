"""JWT token refresh."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Header, HTTPException

from ..config import JWT_EXPIRY_HOURS, REFRESH_THRESHOLD_HOURS, get_jwt_secret
from ..db import users_table

router = APIRouter()


@router.post("/token/refresh")
def refresh_token(authorization: str = Header()):
    """Issue a new JWT when the current one is within the refresh window.

    Accepts tokens that are still valid but close to expiring.
    Rejects tokens that are already expired or still far from expiry.
    The refresh window is defined by ``REFRESH_THRESHOLD_HOURS`` in
    ``app.config``.

    Args:
        authorization: Raw ``Authorization`` header value (``Bearer <token>``).

    Returns:
        A dict containing the newly signed JWT.

    Raises:
        HTTPException: 401 if the token is missing, invalid, or already
            expired.  400 if the token is still far from expiry.  403 if
            the user no longer exists.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization.split(" ", 1)[1]
    secret = get_jwt_secret()

    try:
        payload = jwt.decode(
            token, secret, algorithms=["HS256"], options={"verify_exp": False}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    remaining = exp - now

    if remaining.total_seconds() < 0:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")

    if remaining.total_seconds() > REFRESH_THRESHOLD_HOURS * 3600:
        raise HTTPException(status_code=400, detail="Token still valid, refresh not needed")

    table = users_table()
    result = table.get_item(Key={"user_id": payload["user_id"]})
    if "Item" not in result:
        raise HTTPException(status_code=403, detail="User no longer exists")

    new_payload = {
        "jti": str(uuid.uuid4()),
        "user_id": payload["user_id"],
        "email": payload["email"],
        "client_id": payload.get("client_id"),
        "site_id": payload.get("site_id"),
        "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": now,
    }

    return {"token": jwt.encode(new_payload, secret, algorithm="HS256")}
