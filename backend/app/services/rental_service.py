from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.equipment import Equipment, EquipmentStatus
from ..schemas.equipment import EquipmentUpdate


def update_equipment(db: Session, equipment_id: int, payload: EquipmentUpdate) -> Equipment:
    # 1. Fetch equipment
    equipment = db.get(Equipment, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # 2. Enforce Rule 6: Setting status to Repair on InUse equipment is not allowed
    if payload.status == EquipmentStatus.REPAIR and equipment.status == EquipmentStatus.IN_USE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot set status to Repair on equipment that is In use",
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

    # 3. Delete
    db.delete(equipment)
    db.commit()
