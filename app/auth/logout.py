"""User logout via token blacklisting."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..db import blacklist_table
from .dependencies import get_current_user

router = APIRouter()


@router.post("/logout")
def logout(user: dict = Depends(get_current_user)):
    """Add the current JWT to the blacklist.

    Writes the token's JTI to the ``TokenBlacklist`` table so that
    subsequent requests using the same token are rejected.  The TTL
    matches the token's original expiry so the record auto-deletes.

    Args:
        user: Decoded JWT payload injected by ``get_current_user``.

    Returns:
        A confirmation message.
    """
    table = blacklist_table()
    table.put_item(Item={
        "token_jti": user["jti"],
        "ttl": user["exp"],
        "blacklisted_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"message": "Logged out successfully"}
