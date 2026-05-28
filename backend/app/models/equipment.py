from datetime import date
from enum import Enum

from sqlalchemy import Date, Enum as SAEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class EquipmentStatus(str, Enum):
    AVAILABLE = "Available"
    IN_USE = "In use"
    REPAIR = "Repair"
    ERROR = "Error"


equipment_status_type = SAEnum(
    EquipmentStatus,
    name="equipment_status",
    native_enum=False,
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
    validate_strings=True,
)


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    history: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[EquipmentStatus] = mapped_column(
        equipment_status_type,
        nullable=False,
        default=EquipmentStatus.AVAILABLE,
    )

    rentals: Mapped[list["Rental"]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
    )