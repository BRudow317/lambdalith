"""Health check routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/ghp")
def health_root() -> dict:
    """Basic health response. For the GitHub Pages brudow317.github.io

    Returns:
        ``{"status": "ok"}`` when the Lambda is running.
    """
    return {"status": "ok"}


@router.get("/mlm")
def live() -> dict:
    """Basic health response. For millerlandman.com

    Returns:
        ``{"status": "live"}`` confirming the process is alive.
    """
    return {"status": "live"}


@router.get("/cloudvoyages")
def ready() -> dict:
    """Basic health response for cloudvoyages.com

    Returns:
        ``{"status": "ready"}`` confirming the service can accept traffic.
    """
    return {"status": "ready"}
