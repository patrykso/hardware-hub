from __future__ import annotations

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from .config import settings

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


ALGORITHM = "HS256"
security_scheme = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.access_token_expire_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user