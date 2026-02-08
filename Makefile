.PHONY: docs serve lint test dev

docs:
	pdoc app --output-directory docs

serve:
	uvicorn app.app:app --reload

lint:
	ruff check app/ handler.py
	ruff format --check app/ handler.py

test:
	pytest tests/

dev: serve
