from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import get_current_admin_user
from ..database import Base, engine, get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..seed import seed_database
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    if id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself."
        )
    user_service.delete_user(db, id)


@router.post("/reset-db", status_code=status.HTTP_200_OK)
def reset_database(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        # Close current session before dropping tables
        db.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        from ..database import SessionLocal
        with SessionLocal() as session:
            seed_database(session, force=True)

        return {"status": "success", "message": "Database reset completed."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset database: {str(e)}"
        )
