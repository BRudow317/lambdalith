"""FastAPI routes that wrap legacy Lambda auth handlers."""

from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from . import login as login_handler
from . import logout as logout_handler
from . import pw_reset as pw_reset_handler
from . import pw_reset_confirm as pw_reset_confirm_handler
from . import register_user as register_user_handler
from . import token_refresh as token_refresh_handler

router = APIRouter()


def _to_event(request: Request, body: Optional[str]) -> Dict[str, Any]:
    """Build a minimal API Gateway-style event dict."""
    headers = {k.lower(): v for k, v in request.headers.items()}
    return {
        "headers": headers,
        "body": body,
        "requestContext": {"http": {"method": request.method}},
        "path": request.url.path,
        "queryStringParameters": dict(request.query_params),
    }


def _to_response(result: Dict[str, Any]) -> JSONResponse:
    """Convert a Lambda-style dict response to FastAPI response."""
    status_code = result.get("statusCode", 200)
    headers = result.get("headers") or {}
    body = result.get("body") or ""
    try:
        payload = json.loads(body)
    except (TypeError, json.JSONDecodeError):
        payload = body
    return JSONResponse(status_code=status_code, content=payload, headers=headers)


async def _handle(
    request: Request,
    handler: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> JSONResponse:
    body_bytes = await request.body()
    body = body_bytes.decode("utf-8") if body_bytes else None
    event = _to_event(request, body)
    return _to_response(handler(event))


@router.post("/login")
async def login(request: Request) -> JSONResponse:
    """Authenticate user and return JWT."""
    return await _handle(request, login_handler.login)


@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    """Invalidate the current JWT."""
    return await _handle(request, logout_handler.logout)


@router.post("/register")
async def register(request: Request) -> JSONResponse:
    """Register a new user."""
    return await _handle(request, register_user_handler.register_user)


@router.post("/password-reset")
async def password_reset(request: Request) -> JSONResponse:
    """Send password reset email if account exists."""
    return await _handle(request, pw_reset_handler.pw_reset)


@router.post("/password-reset/confirm")
async def password_reset_confirm(request: Request) -> JSONResponse:
    """Confirm password reset using token."""
    return await _handle(request, pw_reset_confirm_handler.pw_reset_confirm)


@router.post("/token/refresh")
async def refresh_token(request: Request) -> JSONResponse:
    """Refresh an access token near expiry."""
    return await _handle(request, token_refresh_handler.token_refresh)
