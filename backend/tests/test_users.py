import pytest


def test_list_users_non_admin(user_client):
    response = user_client.get("/api/v1/users")
    assert response.status_code == 403


def test_list_users_success(admin_client):
    response = admin_client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    usernames = [u["username"] for u in data]
    assert "admin" in usernames
    assert "user" in usernames
    # Ensure password_hash is not returned in response schemas
    for user in data:
        assert "password" not in user
        assert "password_hash" not in user


def test_create_user_non_admin(user_client):
    payload = {
        "username": "newuser",
        "password": "newpassword",
        "is_admin": False,
    }
    response = user_client.post("/api/v1/users", json=payload)
    assert response.status_code == 403


def test_create_user_success(admin_client):
    payload = {
        "username": "newuser",
        "password": "newpassword",
        "is_admin": False,
    }
    response = admin_client.post("/api/v1/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["is_admin"] is False
    assert "id" in data
    assert "created_at" in data

    # Verify user can log in
    login_resp = admin_client.post(
        "/api/v1/auth/login",
        json={"username": "newuser", "password": "newpassword"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_create_duplicate_user_fails(admin_client):
    payload = {
        "username": "user",  # 'user' already exists in conftest seeding
        "password": "newpassword",
        "is_admin": False,
    }
    response = admin_client.post("/api/v1/users", json=payload)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]
