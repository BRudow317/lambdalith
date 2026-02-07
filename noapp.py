"""Package shim to avoid name collisions with the `app/` package."""

from pathlib import Path

# Treat this module as a namespace package so `import app.app` resolves to `app/app.py`.
__path__ = [str(Path(__file__).parent / "app")]
