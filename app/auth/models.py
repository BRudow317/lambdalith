"""Pydantic request/response models for authentication."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credentials submitted to ``POST /auth/login``."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Payload for ``POST /auth/register``.

    Attributes:
        email: Must be a valid email address.
        password: Minimum 8 characters.
        name: Optional display name.
    """

    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class PasswordResetRequest(BaseModel):
    """Payload for ``POST /auth/password-reset``."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Payload for ``POST /auth/password-reset/confirm``.

    Attributes:
        token: The URL-safe reset token from the email link.
        new_password: Minimum 8 characters.
    """

    token: str
    new_password: str = Field(min_length=8)
