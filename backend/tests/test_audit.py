import sys
import os
import pytest
from datetime import datetime, timedelta, timezone

# Add the mcp_server directory to the system path to allow importing its modules
mcp_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../mcp_server"))
sys.path.insert(0, mcp_server_path)

import server as mcp_server_module
from database import Base, Equipment, Rental, User

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# In-memory SQLite DB for the audit tests
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AuditTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def audit_db():
    # Build tables
    Base.metadata.create_all(bind=test_engine)
    db = AuditTestingSessionLocal()
    
    # Monkey-patch SessionLocal in the server module so it uses our in-memory DB session
    original_session_local = mcp_server_module.SessionLocal
    mcp_server_module.SessionLocal = AuditTestingSessionLocal
    
    try:
        yield db
    finally:
        db.close()
        # Restore the original SessionLocal
        mcp_server_module.SessionLocal = original_session_local
        # Tear down tables
        Base.metadata.drop_all(bind=test_engine)


def test_audit_flags_item_in_repair_beyond_threshold(audit_db):
    # 1. Create a user
    user = User(id=1, username="test_user", is_admin=False)
    audit_db.add(user)
    
    # 2. Create equipment that is in Repair
    eq = Equipment(
        id=1,
        name="Long Repair Phone",
        brand="Apple",
        purchase_date=datetime.now(timezone.utc).date() - timedelta(days=60),
        status="Repair",
    )
    audit_db.add(eq)
    
    # 3. Create a past rental that ended 40 days ago (threshold is 30 days)
    # The last activity will be the returned_at date (40 days ago)
    rental = Rental(
        id=1,
        equipment_id=1,
        user_id=1,
        rented_at=datetime.now(timezone.utc) - timedelta(days=45),
        returned_at=datetime.now(timezone.utc) - timedelta(days=40),
    )
    audit_db.add(rental)
    audit_db.commit()
    
    # Call the audit_inventory tool function directly
    findings = mcp_server_module.audit_inventory()
    
    # We expect long_in_repair to be flagged (and NOT never_rented because it has a rental record)
    assert len(findings) == 1
    finding = findings[0]
    assert finding["equipment_id"] == 1
    assert finding["issue_type"] == "long_in_repair"
    assert finding["severity"] == "warning"
    assert "In Repair" in finding["detail"]


def test_audit_flags_never_rented_item(audit_db):
    # Create equipment that is Available but never rented
    eq = Equipment(
        id=2,
        name="Never Rented Phone",
        brand="Google",
        purchase_date=datetime.now(timezone.utc).date() - timedelta(days=10),
        status="Available",
    )
    audit_db.add(eq)
    audit_db.commit()
    
    # Call the audit_inventory tool function directly
    findings = mcp_server_module.audit_inventory()
    
    # We expect never_rented to be flagged
    assert len(findings) == 1
    finding = findings[0]
    assert finding["equipment_id"] == 2
    assert finding["issue_type"] == "never_rented"
    assert finding["severity"] == "info"
    assert "never" in finding["detail"].lower()


def test_audit_returns_empty_for_clean_inventory(audit_db):
    # Create a user
    user = User(id=1, username="test_user", is_admin=False)
    audit_db.add(user)
    
    # Create a healthy, recently purchased equipment that has been rented recently
    eq = Equipment(
        id=3,
        name="Healthy Tablet",
        brand="Samsung",
        purchase_date=datetime.now(timezone.utc).date() - timedelta(days=5),
        status="Available",
    )
    audit_db.add(eq)
    
    # Create a recent completed rental
    rental = Rental(
        id=2,
        equipment_id=3,
        user_id=1,
        rented_at=datetime.now(timezone.utc) - timedelta(days=3),
        returned_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    audit_db.add(rental)
    audit_db.commit()
    
    # Call the audit_inventory tool function directly
    findings = mcp_server_module.audit_inventory()
    
    # We expect no findings for this clean item
    assert len(findings) == 0
