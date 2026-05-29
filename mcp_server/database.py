import os
from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Load environment variables
load_dotenv()

# Determine DB Path and build read-only URL
db_path = os.getenv("DB_PATH", "../backend/hub.db")

if db_path.startswith("sqlite://"):
    # Ensure read-only mode is active if using SQLite
    if "mode=ro" not in db_path:
        if "?" in db_path:
            db_path += "&mode=ro"
        else:
            db_path += "?mode=ro"
    DATABASE_URL = db_path
else:
    path = Path(db_path)
    if not path.is_absolute():
        # Resolve relative to the repository root (parent of mcp_server)
        path = Path(__file__).resolve().parent.parent / path
    
    DATABASE_URL = f"sqlite:///{path.resolve().as_posix()}?mode=ro"

# Initialize SQLAlchemy read-only engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=False, default="")
    purchase_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Available")

    rentals = relationship("Rental", back_populates="equipment", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    rentals = relationship("Rental", back_populates="user", cascade="all, delete-orphan")


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rented_at = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)

    equipment = relationship("Equipment", back_populates="rentals")
    user = relationship("User", back_populates="rentals")
