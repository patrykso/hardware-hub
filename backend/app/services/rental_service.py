from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.equipment import Equipment, EquipmentStatus
from ..models.rental import Rental
from ..models.user import User
from ..schemas.equipment import EquipmentUpdate


def update_equipment(db: Session, equipment_id: int, payload: EquipmentUpdate) -> Equipment:
    # 1. Fetch equipment
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # 2. Enforce guards on status updates to prevent state mismatch
    if payload.status is not None:
        if equipment.status == EquipmentStatus.IN_USE and payload.status != EquipmentStatus.IN_USE:
            if payload.status == EquipmentStatus.REPAIR:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot set status to Repair on equipment that is In use",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot change status on equipment that is In use. It must be returned first.",
            )
        if payload.status == EquipmentStatus.IN_USE and equipment.status != EquipmentStatus.IN_USE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot manually set status to In use.",
            )

    # 3. Apply updates
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(equipment, field, value)

    db.commit()
    db.refresh(equipment)
    return equipment


def delete_equipment(db: Session, equipment_id: int) -> None:
    # 1. Fetch equipment
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # 2. Enforce Rule 5: Cannot delete equipment that is InUse
    if equipment.status == EquipmentStatus.IN_USE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete equipment that is currently In use",
        )

    open_rental = db.scalar(
        select(Rental).where(
            Rental.equipment_id == equipment_id,
            Rental.returned_at == None,
        )
    )
    if open_rental:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete equipment that has an active rental",
        )

    # 3. Delete
    db.delete(equipment)
    db.commit()


def rent_equipment(db: Session, equipment_id: int, user_id: int) -> Rental:
    # 1. Fetch equipment
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # 2. Enforce Rule 1: Cannot rent if status is not Available
    if equipment.status != EquipmentStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot rent equipment that is not Available",
        )

    # 3. Enforce Rule 2: Cannot rent if the equipment already has an open rental (defensive check)
    open_rental = db.scalar(
        select(Rental).where(
            Rental.equipment_id == equipment_id,
            Rental.returned_at == None,
        )
    )
    if open_rental:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Equipment already has an open rental",
        )

    # 4. Update equipment status
    equipment.status = EquipmentStatus.IN_USE

    # 5. Create rental
    rental = Rental(
        equipment_id=equipment_id,
        user_id=user_id,
        rented_at=datetime.now(timezone.utc),
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


def return_equipment(db: Session, rental_id: int, user: User) -> Rental:
    # 1. Fetch rental
    rental = db.get(Rental, rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    # 2. Enforce Rule 3: Cannot return equipment that has no open rental
    if rental.returned_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rental has already been returned",
        )

    # 3. Enforce Rule 4: Cannot return equipment rented by a different user (unless admin)
    if not user.is_admin and rental.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot return equipment rented by another user",
        )

    # 4. Fetch and update equipment status
    equipment = db.get(Equipment, rental.equipment_id)
    if equipment:
        equipment.status = EquipmentStatus.AVAILABLE

    # 5. Set returned_at
    rental.returned_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rental)
    return rental


def list_rentals(db: Session, user: User) -> list[Rental]:
    if user.is_admin:
        query = select(Rental).order_by(Rental.rented_at.desc())
    else:
        query = select(Rental).where(Rental.user_id == user.id).order_by(Rental.rented_at.desc())
    return list(db.execute(query).scalars().all())
