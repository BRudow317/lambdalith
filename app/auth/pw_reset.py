"""Password reset request."""

import secrets
from datetime import datetime, timedelta, timezone

import boto3
from fastapi import APIRouter, Depends

from ..db import password_reset_table, users_table
from .dependencies import get_tenant
from .models import PasswordResetRequest

router = APIRouter()

GENERIC_RESPONSE = {"message": "If account exists, reset email sent"}


@router.post("/password-reset")
def password_reset(body: PasswordResetRequest, tenant: dict = Depends(get_tenant)):
    """Generate a password reset token and send an email.

    Creates a URL-safe reset token, stores it in the
    ``PasswordResetTokens`` table with a one-hour TTL, and sends an
    email via SES containing the reset link.

    A generic response is returned regardless of whether the email
    matches an existing user, to prevent user-enumeration attacks.

    Args:
        body: Validated payload containing the user's email address.
        tenant: Tenant context resolved from the ``x-api-key`` header.

    Returns:
        A generic acknowledgement message.
    """
    table = users_table()
    reset_table = password_reset_table()
    email = body.email.lower()
    user_id = f"{tenant['client_id']}#{tenant['site_id']}#{email}"

    try:
        result = table.get_item(Key={"user_id": user_id})
    except Exception:
        return GENERIC_RESPONSE

    if "Item" not in result:
        return GENERIC_RESPONSE

    reset_token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_table.put_item(Item={
        "reset_token": reset_token,
        "user_id": user_id,
        "ttl": int(expiry.timestamp()),
        "used": False,
    })

    """TODO: SES email setup and sending """
    # reset_link = f"https://{tenant['site_id'].lower()}.com/reset-password?token={reset_token}"
    # ses = boto3.client("ses")
    # ses.send_email(
    #     Source="noreply@yourservice.com",
    #     Destination={"ToAddresses": [email]},
    #     Message={
    #         "Subject": {"Data": "Password Reset Request"},
    #         "Body": {"Text": {"Data": f"Click here to reset: {reset_link}"}},
    #     },
    # )
    print(f"Password reset token for {email}: {reset_token} (expires at {expiry.isoformat()})")

    return GENERIC_RESPONSE
