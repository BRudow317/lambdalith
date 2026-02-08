"""Auth service router combining all auth endpoints."""

from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .pw_reset import router as pw_reset_router
from .pw_reset_confirm import router as pw_reset_confirm_router
from .register_user import router as register_router
from .token_refresh import router as token_refresh_router

router = APIRouter()
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(register_router)
router.include_router(pw_reset_router)
router.include_router(pw_reset_confirm_router)
router.include_router(token_refresh_router)
