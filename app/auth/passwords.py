"""Password hashing helpers using hashlib.scrypt."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Tuple


SCRYPT_N = 16384
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_SALT_BYTES = 16
SCRYPT_DKLEN = 32


def _encode_bytes(value: bytes) -> str:
    """Base64-encode raw bytes for storage."""
    return base64.b64encode(value).decode("ascii")


def _decode_bytes(value: str) -> bytes:
    """Decode base64-encoded bytes stored as ASCII text."""
    return base64.b64decode(value.encode("ascii"))


def _split_hash(value: str) -> Tuple[int, int, int, bytes, bytes]:
    """Parse the stored hash into scrypt parameters and byte values."""
    parts = value.split("$")
    if len(parts) != 6 or parts[0] != "scrypt":
        raise ValueError("Unsupported password hash format")
    n = int(parts[1])
    r = int(parts[2])
    p = int(parts[3])
    salt = _decode_bytes(parts[4])
    digest = _decode_bytes(parts[5])
    return n, r, p, salt, digest


def hash_password(password: str) -> str:
    """Hash a password with scrypt and return a self-describing string.

    The output format is ``scrypt$N$r$p$salt$digest`` where salt and
    digest are base64-encoded.  This makes the hash portable and
    allows parameter upgrades without breaking existing records.

    Args:
        password: The plaintext password to hash.

    Returns:
        A ``$``-delimited string encoding the scrypt parameters, salt,
        and derived key.
    """
    salt = secrets.token_bytes(SCRYPT_SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return "scrypt$" + "$".join(
        [
            str(SCRYPT_N),
            str(SCRYPT_R),
            str(SCRYPT_P),
            _encode_bytes(salt),
            _encode_bytes(digest),
        ]
    )


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored scrypt hash.

    Re-derives the key using the parameters and salt embedded in the
    stored hash, then compares using constant-time ``hmac.compare_digest``
    to prevent timing attacks.

    Args:
        password: The plaintext password to verify.
        stored_hash: The self-describing hash string from ``hash_password``.

    Returns:
        ``True`` if the password matches, ``False`` otherwise.
    """
    try:
        n, r, p, salt, digest = _split_hash(stored_hash)
    except (ValueError, TypeError):
        return False

    candidate = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=n,
        r=r,
        p=p,
        dklen=len(digest),
    )
    return hmac.compare_digest(candidate, digest)
