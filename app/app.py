"""FastAPI application setup for the Lambda handler."""

from fastapi import FastAPI

from .admin.routes import router as admin_router
from .auth.routes import router as auth_router
from .entity.routes import router as entity_router
from .health.routes import router as health_router

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Basic health endpoint for smoke tests.

    Returns:
        ``{"ok": True}`` when the application is loaded.
    """
    return {"ok": True}


def register_routes(target: FastAPI) -> None:
    """Attach feature routers to the application.

    Each service package exposes a single ``router`` that is mounted
    under its own URL prefix.

    Args:
        target: The FastAPI application instance to register routes on.
    """
    target.include_router(auth_router, prefix="/auth")
    target.include_router(admin_router, prefix="/admin")
    target.include_router(entity_router, prefix="/user")
    target.include_router(health_router, prefix="/health")


register_routes(app)
