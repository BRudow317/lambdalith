"""User routes."""

from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_user

router = APIRouter()

@router.get("/user")
def get_user(user: dict = Depends(get_current_user)) -> dict:
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


@router.post("/user")
def ready() -> dict:
    """Readiness probe.

    Returns:
        ``{"status": "ready"}`` confirming the service can accept traffic.
    """
    return {"status": "ready"}

"""Entity service router.

from fastapi import APIRouter

from .user_profile import router as user_profile_router

router = APIRouter()
router.include_router(user_profile_router)
"""


