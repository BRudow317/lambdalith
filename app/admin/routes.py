"""Admin SSR form routes using Jinja2 templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from ..auth.dependencies import get_current_user, resolve_tenant
from ..auth.models import PasswordResetRequest, RegisterRequest
from ..auth.pw_reset import password_reset as password_reset_handler
from ..auth.register_user import register as register_handler

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router = APIRouter()


def _base_context(request: Request, user: dict) -> Dict[str, Any]:
    return {
        "request": request,
        "title": "Admin",
        "user_email": user.get("email"),
    }


@router.get("/users", response_class=HTMLResponse)
def users_form(
    request: Request,
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render the basic user management form.

    Args:
        request: The incoming HTTP request object.
        user: Decoded JWT payload injected by ``get_current_user``.

    Returns:
        An HTML response containing the user management form.
    """
    context = _base_context(request, user)
    return templates.TemplateResponse("admin/users_form.html", context)


@router.post("/users", response_class=HTMLResponse)
def submit_user_form(
    request: Request,
    email: EmailStr = Form(...),
    api_key: str = Form(...),
    password: str = Form(...),
    name: str = Form(""),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Handle the user management form submission.

    Args:
        request: The incoming HTTP request object.
        email: Email address submitted from the form.
        api_key: Tenant API key for resolving the target tenant.
        password: Plaintext password for the new user.
        name: Optional display name.
        user: Decoded JWT payload injected by ``get_current_user``.

    Returns:
        An HTML response showing the submitted values.
    """
    context = _base_context(request, user)
    try:
        tenant = resolve_tenant(api_key)
        result = register_handler(RegisterRequest(
            email=email,
            password=password,
            name=name,
        ), tenant)
        summary = result.get("message", "Registration completed.")
        fields = {
            "email": email,
            "name": name,
            "client_id": tenant.get("client_id"),
            "site_id": tenant.get("site_id"),
        }
        status_code = 200
    except HTTPException as exc:
        summary = exc.detail
        fields = {"email": email}
        status_code = exc.status_code

    context.update({
        "title": "User Submitted",
        "summary": summary,
        "fields": fields,
    })
    return templates.TemplateResponse(
        "admin/result.html",
        context,
        status_code=status_code,
    )


@router.get("/password-reset", response_class=HTMLResponse)
def password_reset_form(
    request: Request,
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Render the password reset request form.

    Args:
        request: The incoming HTTP request object.
        user: Decoded JWT payload injected by ``get_current_user``.

    Returns:
        An HTML response containing the reset request form.
    """
    context = _base_context(request, user)
    return templates.TemplateResponse("admin/password_reset_form.html", context)


@router.post("/password-reset", response_class=HTMLResponse)
def submit_password_reset_form(
    request: Request,
    email: EmailStr = Form(...),
    api_key: str = Form(...),
    user: dict = Depends(get_current_user),
) -> HTMLResponse:
    """Handle password reset request submissions.

    Args:
        request: The incoming HTTP request object.
        email: Email address submitted from the form.
        api_key: Tenant API key for resolving the target tenant.
        user: Decoded JWT payload injected by ``get_current_user``.

    Returns:
        An HTML response showing the submitted values.
    """
    context = _base_context(request, user)
    try:
        tenant = resolve_tenant(api_key)
        result = password_reset_handler(PasswordResetRequest(email=email), tenant)
        summary = result.get("message", "Password reset request received.")
        fields = {
            "email": email,
            "client_id": tenant.get("client_id"),
            "site_id": tenant.get("site_id"),
        }
        status_code = 200
    except HTTPException as exc:
        summary = exc.detail
        fields = {"email": email}
        status_code = exc.status_code

    context.update({
        "title": "Reset Submitted",
        "summary": summary,
        "fields": fields,
    })
    return templates.TemplateResponse(
        "admin/result.html",
        context,
        status_code=status_code,
    )
