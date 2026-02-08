"""User registration."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from ..db import users_table
from .dependencies import get_tenant
from .models import RegisterRequest
from .passwords import hash_password

router = APIRouter()


@router.post("/register", status_code=201)
def register(body: RegisterRequest, tenant: dict = Depends(get_tenant)):
    """Register a new user in the tenant-scoped Users table.

    Builds a composite ``user_id`` from the tenant's client/site IDs and the
    email address, then writes the record to DynamoDB.  Duplicate emails
    within the same tenant are rejected.

    Args:
        body: Validated registration payload (email, password, optional name).
        tenant: Tenant context resolved from the ``x-api-key`` header.

    Returns:
        A 201 response with a confirmation message and the new user's ID.

    Raises:
        HTTPException: 409 if a user with the same tenant-scoped email
            already exists.
    """
    table = users_table()
    email = body.email.lower()
    user_id = f"{tenant['client_id']}#{tenant['site_id']}#{email}"

    existing = table.get_item(Key={"user_id": user_id})
    if "Item" in existing:
        raise HTTPException(status_code=409, detail="User already exists")

    now = datetime.now(timezone.utc).isoformat()
    table.put_item(Item={
        "user_id": user_id,
        "email": email,
        "password_hash": hash_password(body.password),
        "name": body.name,
        "client_id": tenant["client_id"],
        "site_id": tenant["site_id"],
        "created_at": now,
        "updated_at": now,
    })

    return {
        "message": "Registration successful",
        "user": {"user_id": user_id, "email": email, "name": body.name},
    }
