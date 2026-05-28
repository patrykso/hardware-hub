import pytest
from fastapi import APIRouter, Depends
from jose import jwt

from app.core.config import settings
from app.core.security import get_current_admin_user, get_current_user
from app.main import app
from app.models.user import User

# Define custom test router to check dependency behaviors directly
debug_router = APIRouter(prefix="/test-auth", tags=["test-auth"])


@debug_router.get("/me")
def route_get_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "is_admin": current_user.is_admin}


@debug_router.get("/admin")
def route_get_admin(admin_user: User = Depends(get_current_admin_user)):
    return {"username": admin_user.username, "is_admin": admin_user.is_admin}


# Auto-register test router for this test module execution
app.include_router(debug_router)



def test_login_success(client):
    """Test standard login with correct credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "user", "password": "user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Decode and verify the payload
    payload = jwt.decode(data["access_token"], settings.secret_key, algorithms=["HS256"])
    assert payload["sub"] == "user"
    assert payload["is_admin"] is False


def test_login_success_admin(client):
    """Test admin login with correct credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    payload = jwt.decode(data["access_token"], settings.secret_key, algorithms=["HS256"])
    assert payload["sub"] == "admin"
    assert payload["is_admin"] is True


def test_login_invalid_password(client):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "user", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_non_existent_user(client):
    """Test login with a non-existent username."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "user"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_current_user_valid_token(user_client):
    """Test get_current_user dependency with a valid user token."""
    response = user_client.get("/test-auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert data["is_admin"] is False


def test_get_current_user_valid_admin_token(admin_client):
    """Test get_current_user dependency with a valid admin token."""
    response = admin_client.get("/test-auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["is_admin"] is True


def test_get_current_user_invalid_token(client):
    """Test get_current_user dependency with an invalid/malformed token."""
    headers = {"Authorization": "Bearer not-a-valid-token"}
    response = client.get("/test-auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_get_current_user_missing_token(client):
    """Test get_current_user dependency with missing Authorization header."""
    response = client.get("/test-auth/me")
    # FastAPI HTTPBearer returns 401 when token is missing entirely
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"



def test_get_current_admin_user_success(admin_client):
    """Test get_current_admin_user dependency with a valid admin token."""
    response = admin_client.get("/test-auth/admin")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["is_admin"] is True


def test_get_current_admin_user_forbidden(user_client):
    """Test get_current_admin_user dependency with a non-admin token (user)."""
    response = user_client.get("/test-auth/admin")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_get_current_admin_user_invalid_token(client):
    """Test get_current_admin_user dependency with an invalid token."""
    headers = {"Authorization": "Bearer not-a-valid-token"}
    response = client.get("/test-auth/admin", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
