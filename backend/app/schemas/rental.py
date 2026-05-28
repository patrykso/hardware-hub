from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RentalBase(BaseModel):
    equipment_id: int


class RentalCreate(RentalBase):
    pass


class RentalRead(RentalBase):
    id: int
    user_id: int
    rented_at: datetime
    returned_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
