"""Health check routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_root() -> dict:
    """Basic health response."""
    return {"status": "ok"}


@router.get("/live")
def live() -> dict:
    """Liveness probe."""
    return {"status": "live"}


@router.get("/ready")
def ready() -> dict:
    """Readiness probe."""
    return {"status": "ready"}
