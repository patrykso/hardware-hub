from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..database import get_db
from ..models.rental import Rental
from ..models.user import User
from ..schemas.rental import RentalCreate, RentalRead
from ..services import rental_service

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.post("", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
def rent_equipment(
    payload: RentalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Rental:
    return rental_service.rent_equipment(
        db,
        equipment_id=payload.equipment_id,
        user_id=current_user.id,
    )


@router.post("/{id}/return", response_model=RentalRead)
def return_equipment(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Rental:
    return rental_service.return_equipment(db, rental_id=id, user=current_user)


@router.get("", response_model=List[RentalRead])
def list_rentals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Rental]:
    return rental_service.list_rentals(db, user=current_user)
