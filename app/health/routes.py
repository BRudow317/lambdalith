"""Health check routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_root() -> dict:
    """Basic health response.

    Returns:
        ``{"status": "ok"}`` when the Lambda is running.
    """
    return {"status": "ok"}


@router.get("/live")
def live() -> dict:
    """Liveness probe.

    Returns:
        ``{"status": "live"}`` confirming the process is alive.
    """
    return {"status": "live"}


@router.get("/ready")
def ready() -> dict:
    """Readiness probe.

    Returns:
        ``{"status": "ready"}`` confirming the service can accept traffic.
    """
    return {"status": "ready"}
