"""User login and JWT token generation."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException

from ..config import JWT_EXPIRY_HOURS, get_jwt_secret
from ..db import users_table
from .dependencies import get_tenant
from .models import LoginRequest
from .passwords import verify_password

router = APIRouter()


"""
TODO: 
    Use a JWT cookie not a json body response, 
to support browser-based clients and SSR forms. 
This will require CORS adjustments and CSRF protections, 
but is more realistic for a full-stack app. The current 
token-in-body approach is more of an API-only style and 
doesn't demonstrate the full capabilities of FastAPI's 
cookie handling or server-rendered forms.
"""
@router.post("/login")
def login(body: LoginRequest, tenant: dict = Depends(get_tenant)):
    """Authenticate a user and return a signed JWT.

    Looks up the user by tenant-scoped ID, verifies the password hash,
    and issues a 24-hour access token with a unique JTI for revocation
    support.

    Args:
        body: Validated login credentials (email and password).
        tenant: Tenant context resolved from the ``x-api-key`` header.

    Returns:
        A dict containing the signed JWT and basic user profile fields.

    Raises:
        HTTPException: 401 if the user does not exist or the password
            is incorrect.
    """
    table = users_table()
    email = body.email.lower()
    user_id = f"{tenant['client_id']}#{tenant['site_id']}#{email}"

    result = table.get_item(Key={"user_id": user_id})
    if "Item" not in result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = result["Item"]
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    now = datetime.now(timezone.utc)
    payload = {
        "jti": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "email": user["email"],
        "client_id": tenant["client_id"],
        "site_id": tenant["site_id"],
        "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": now,
    }
    token = jwt.encode(payload, get_jwt_secret(), algorithm="HS256")

    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET last_login = :t",
        ExpressionAttributeValues={":t": now.isoformat()},
    )

    return {
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user.get("name", ""),
        },
    }
