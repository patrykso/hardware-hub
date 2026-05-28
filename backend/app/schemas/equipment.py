from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from ..models.equipment import EquipmentStatus


class EquipmentBase(BaseModel):
    name: str
    brand: str
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None
    history: Optional[str] = None
    assigned_to: Optional[str] = None
    status: EquipmentStatus = EquipmentStatus.AVAILABLE


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None
    history: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[EquipmentStatus] = None


class EquipmentRead(EquipmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
