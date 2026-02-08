"""Password reset confirmation."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..db import password_reset_table, users_table
from .models import PasswordResetConfirm
from .passwords import hash_password

router = APIRouter()


@router.post("/password-reset/confirm")
def password_reset_confirm(body: PasswordResetConfirm):
    """Reset a password using a valid reset token.

    Validates the token against the ``PasswordResetTokens`` table,
    hashes the new password, and updates the user record.  The token
    is marked as used to prevent replay.

    Args:
        body: Validated payload containing the reset token and new password.

    Returns:
        A confirmation message on success.

    Raises:
        HTTPException: 400 if the token is invalid, expired, or already used.
    """
    reset_table = password_reset_table()

    result = reset_table.get_item(Key={"reset_token": body.token})
    if "Item" not in result:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    token_data = result["Item"]

    if token_data.get("used", False):
        raise HTTPException(status_code=400, detail="Token already used")

    if datetime.now(timezone.utc).timestamp() > token_data["ttl"]:
        raise HTTPException(status_code=400, detail="Token expired")

    table = users_table()
    now = datetime.now(timezone.utc).isoformat()

    table.update_item(
        Key={"user_id": token_data["user_id"]},
        UpdateExpression="SET password_hash = :h, updated_at = :u",
        ExpressionAttributeValues={
            ":h": hash_password(body.new_password),
            ":u": now,
        },
    )

    reset_table.update_item(
        Key={"reset_token": body.token},
        UpdateExpression="SET used = :u",
        ExpressionAttributeValues={":u": True},
    )

    return {"message": "Password reset successful"}
