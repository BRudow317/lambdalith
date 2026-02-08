"""User profile endpoint."""

from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_user

router = APIRouter()


@router.get("/me")
def get_profile(user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile from the JWT claims.

    Args:
        user: Decoded JWT payload injected by ``get_current_user``.

    Returns:
        A dict containing the user's ID, email, client, and site.
    """
    return {
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "client_id": user.get("client_id"),
            "site_id": user.get("site_id"),
        }
    }
