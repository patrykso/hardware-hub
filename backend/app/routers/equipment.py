from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.security import get_current_admin_user, get_current_user
from ..database import get_db
from ..models.equipment import Equipment, EquipmentStatus
from ..models.user import User
from ..schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate
from ..services import rental_service

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=List[EquipmentRead])
def list_equipment(
    status: Optional[EquipmentStatus] = None,
    brand: Optional[str] = None,
    sort_by: str = "id",
    order: str = "asc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Equipment]:
    # 1. Base query
    query = select(Equipment)

    # 2. Filter by status
    if status is not None:
        query = query.where(Equipment.status == status)

    # 3. Filter by brand
    if brand is not None:
        query = query.where(Equipment.brand == brand)

    # 4. Sorting & Ordering
    valid_sort_fields = {"id", "name", "brand", "purchase_date", "status"}
    if sort_by not in valid_sort_fields:
        sort_by = "id"

    if order not in {"asc", "desc"}:
        order = "asc"

    sort_column = getattr(Equipment, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # 5. Fetch and return results
    results = db.execute(query).scalars().all()
    return list(results)


@router.post("", response_model=EquipmentRead, status_code=status.HTTP_201_CREATED)
def create_equipment(
    payload: EquipmentCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Equipment:
    db_equipment = Equipment(**payload.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.patch("/{id}", response_model=EquipmentRead)
def patch_equipment(
    id: int,
    payload: EquipmentUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Equipment:
    return rental_service.update_equipment(db, equipment_id=id, payload=payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(
    id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    rental_service.delete_equipment(db, equipment_id=id)
