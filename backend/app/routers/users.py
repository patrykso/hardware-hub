from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import get_current_admin_user
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> User:
    return user_service.create_user(db, payload)


@router.get("", response_model=List[UserRead])
def list_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> List[User]:
    users = db.execute(select(User)).scalars().all()
    return list(users)
