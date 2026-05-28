from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .core.config import settings
from .core.security import hash_password
from .database import SessionLocal
from .models import Equipment, EquipmentStatus, User


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

    return EquipmentStatus.AVAILABLE


def _parse_purchase_date(raw_value: object) -> date | None:
    if raw_value in (None, ""):
        return None

    if isinstance(raw_value, date):
        return raw_value

    try:
        return date.fromisoformat(str(raw_value))
    except ValueError:
        return None


def seed_database(session: Session | None = None) -> None:
    owns_session = session is None
    session = session or SessionLocal()

    try:
        equipment_count = session.scalar(select(func.count()).select_from(Equipment)) or 0
        if equipment_count == 0:
            seed_data = json.loads(_seed_file_path().read_text(encoding="utf-8"))
            session.add_all(
                Equipment(
                    name=str(item.get("name", "")).strip(),
                    brand=str(item.get("brand", "")).strip(),
                    purchase_date=_parse_purchase_date(item.get("purchaseDate")),
                    status=_normalize_status(item.get("status")),
                )
                for item in seed_data
            )

        admin_count = session.scalar(select(func.count()).select_from(User).where(User.is_admin.is_(True))) or 0
        if admin_count == 0:
            session.add(
                User(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    is_admin=True,
                )
            )

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if owns_session:
            session.close()