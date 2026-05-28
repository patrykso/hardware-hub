from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import hash_password
from ..models.user import User
from ..schemas.user import UserCreate


def create_user(db: Session, payload: UserCreate) -> User:
    # 1. Check if user already exists
    existing_user = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # 2. Hash password and construct user object
    db_user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_admin=payload.is_admin,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
