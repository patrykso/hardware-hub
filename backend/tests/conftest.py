import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models.equipment import Equipment, EquipmentStatus
from app.models.user import User

# In-memory SQLite for high-speed, isolated test runs
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="db_session")
def fixture_db_session():
    # Construct tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed users (password is 'password123')
        admin_pwd = "password123"
        user_pwd = "password123"
        admin = User(
            username="admin1",
            password_hash=hash_password(admin_pwd),
            is_admin=True,
        )
        regular = User(
            username="user1",
            password_hash=hash_password(user_pwd),
            is_admin=False,
        )
        db.add(admin)
        db.add(regular)

        # Seed equipment in various statuses
        eq_available = Equipment(
            id=1,
            name="iPhone Available",
            brand="Apple",
            status=EquipmentStatus.AVAILABLE,
        )
        eq_in_use = Equipment(
            id=2,
            name="MacBook InUse",
            brand="Apple",
            status=EquipmentStatus.IN_USE,
        )
        eq_repair = Equipment(
            id=3,
            name="Mouse Repair",
            brand="Razer",
            status=EquipmentStatus.REPAIR,
        )
        db.add(eq_available)
        db.add(eq_in_use)
        db.add(eq_repair)

        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def fixture_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token():
    return create_access_token({"sub": "admin1", "is_admin": True})


@pytest.fixture
def user_token():
    return create_access_token({"sub": "user1", "is_admin": False})


@pytest.fixture
def admin_client(client, admin_token):
    # Set default bearer auth header
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client


@pytest.fixture
def user_client(client, user_token):
    # Set default bearer auth header
    client.headers.update({"Authorization": f"Bearer {user_token}"})
    return client
