# controller.py
from auth.routes import router as auth_router
from health.routes import router as health_router
from messages.routes import router as messages_router

def register_routes(app):
    app.include_router(auth_router, prefix="/auth")
    app.include_router(health_router, prefix="/health")
    app.include_router(messages_router, prefix="/messages")