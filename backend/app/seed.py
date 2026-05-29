from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .core.config import settings
from .core.security import hash_password
from .database import SessionLocal
from .models import Equipment, EquipmentStatus, User, Rental


def _seed_file_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "initial_data.json"


def _normalize_status(raw_status: object) -> EquipmentStatus:
    if isinstance(raw_status, EquipmentStatus):
        return raw_status

    normalized = str(raw_status or "").strip().lower().replace(" ", "").replace("_", "")
    if normalized == "inuse":
        return EquipmentStatus.IN_USE
    if normalized == "repair":
        return EquipmentStatus.REPAIR
    if normalized == "available":
        return EquipmentStatus.AVAILABLE

    return EquipmentStatus.ERROR


def _parse_purchase_date(raw_value: object) -> date | None:
    if raw_value in (None, ""):
        return None

    if isinstance(raw_value, date):
        return raw_value

    try:
        return date.fromisoformat(str(raw_value))
    except ValueError:
        return None


def _string_or_none(raw_value: object) -> str | None:
    if raw_value is None:
        return None

    text = str(raw_value).strip()
    return text or None


def _existing_equipment_by_id(session: Session) -> dict[int, Equipment]:
    existing_rows = session.execute(select(Equipment)).scalars().all()
    return {row.id: row for row in existing_rows}


def _parse_source_id(raw_value: object) -> int | None:
    try:
        identifier = int(raw_value)
    except (TypeError, ValueError):
        return None

    return identifier if identifier > 0 else None


def _next_available_id(used_ids: set[int]) -> int:
    candidate = 1
    while candidate in used_ids:
        candidate += 1
    return candidate


def seed_database(session: Session | None = None, force: bool = False) -> None:
    owns_session = session is None
    session = session or SessionLocal()

    try:
        if force:
            # Clear all data if force is True
            session.query(Rental).delete()
            session.query(Equipment).delete()
            session.query(User).delete()
            session.commit()

        # Check if equipment table has data
        equipment_count = session.query(func.count(Equipment.id)).scalar() or 0

        if force or equipment_count == 0:
            # Seed equipment from initial_data.json
            seed_data = json.loads(_seed_file_path().read_text(encoding="utf-8"))
            existing_rows = _existing_equipment_by_id(session)
            used_ids: set[int] = set(existing_rows)

            for item in seed_data:
                source_id = _parse_source_id(item.get("id"))
                purchase_date = _parse_purchase_date(item.get("purchaseDate"))
                status = _normalize_status(item.get("status"))

                had_error = False
                if source_id is None or source_id in used_ids:
                    had_error = True
                    source_id = _next_available_id(used_ids)

                if purchase_date is None and item.get("purchaseDate") is not None:
                    had_error = True

                if status is EquipmentStatus.ERROR:
                    had_error = True

                used_ids.add(source_id)

                equipment = existing_rows.get(source_id)
                if equipment is None:
                    equipment = Equipment(id=source_id)
                    session.add(equipment)
                    existing_rows[source_id] = equipment

                equipment.name = _string_or_none(item.get("name")) or ""
                equipment.brand = _string_or_none(item.get("brand")) or ""
                
                raw_serial = item.get("serialNumber") or item.get("serial_number")
                if raw_serial:
                    equipment.serial_number = _string_or_none(raw_serial)
                else:
                    brand_prefix = (item.get("brand") or "DEV").strip()[:3].upper()
                    equipment.serial_number = f"HUB-{brand_prefix}-{str(source_id).zfill(3)}"

                equipment.purchase_date = purchase_date
                equipment.notes = _string_or_none(item.get("notes"))
                equipment.history = _string_or_none(item.get("history"))
                equipment.assigned_to = _string_or_none(item.get("assignedTo"))
                equipment.status = EquipmentStatus.ERROR if had_error else status

        # Always ensure seed admin user exists
        admin_user = session.execute(select(User).where(User.username == settings.admin_username)).scalar_one_or_none()
        if admin_user is None:
            session.add(
                User(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    is_admin=True,
                )
            )
        else:
            admin_user.password_hash = hash_password(settings.admin_password)
            admin_user.is_admin = True

        # Always ensure seed default regular user exists
        regular_username = "user"
        regular_password = "user"
        regular_user = session.execute(select(User).where(User.username == regular_username)).scalar_one_or_none()
        if regular_user is None:
            session.add(
                User(
                    username=regular_username,
                    password_hash=hash_password(regular_password),
                    is_admin=False,
                )
            )
        else:
            regular_user.password_hash = hash_password(regular_password)
            regular_user.is_admin = False

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if owns_session:
            session.close()