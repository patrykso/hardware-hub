from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .core.config import settings


class Base(DeclarativeBase):
    pass


def _build_database_url(db_path: str) -> str:
    if db_path.startswith("sqlite://"):
        return db_path

    path = Path(db_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[1] / path

    return f"sqlite:///{path.as_posix()}"


engine = create_engine(
    _build_database_url(settings.db_path),
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)