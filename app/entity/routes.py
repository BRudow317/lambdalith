"""Entity service router."""

from fastapi import APIRouter

from .user_profile import router as user_profile_router

router = APIRouter()
router.include_router(user_profile_router)
