"""Leads Routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/lead")
def live() -> dict:
    """Liveness probe.

    Returns:
        ``{"status": "live"}`` confirming the process is alive.
    """
    return {"status": "live"}


@router.post("/lead")
def ready() -> dict:
    """Readiness probe.

    Returns:
        ``{"status": "ready"}`` confirming the service can accept traffic.
    """
    return {"status": "ready"}
