"""Lambda entrypoint wrapper"""

from mangum import Mangum

from app.app import app

handler = Mangum(app)
