"""Lambda entrypoint wrapping the FastAPI app."""

from mangum import Mangum

from app.app import app

handler = Mangum(app)
