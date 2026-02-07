"""FastAPI application setup for the Lambda handler."""

from fastapi import FastAPI

from .auth.routes import router as auth_router
from .health.routes import router as health_router

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Basic health endpoint for smoke tests."""
    return {"ok": True}


def register_routes(target: FastAPI) -> None:
    """Attach feature routers."""
    target.include_router(auth_router, prefix="/auth")
    target.include_router(health_router, prefix="/health")


register_routes(app)
