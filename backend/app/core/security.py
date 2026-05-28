from __future__ import annotations

from passlib.context import CryptContext

try:
    import bcrypt as _bcrypt
except ImportError:  # pragma: no cover - fallback is only used when bcrypt is available.
    _bcrypt = None


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_use_passlib_bcrypt = _bcrypt is not None and hasattr(_bcrypt, "__about__")


def hash_password(password: str) -> str:
    if _use_passlib_bcrypt:
        try:
            return password_context.hash(password)
        except Exception:
            pass

    if _bcrypt is None:
        raise RuntimeError("bcrypt is not available")

    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    if _use_passlib_bcrypt:
        try:
            return password_context.verify(plain_password, password_hash)
        except Exception:
            pass

    if _bcrypt is None:
        raise RuntimeError("bcrypt is not available")

    try:
        return _bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False