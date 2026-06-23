import pytest
from app.models.equipment import EquipmentStatus


def test_cannot_rent_equipment_in_repair(client, user_token):
    # Equipment 3 is "Mouse Repair" (status=REPAIR)
    payload = {"equipment_id": 3}
    response = client.post(
        "/api/v1/rentals",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 409
    assert "Cannot rent equipment that is not Available" in response.json()["detail"]


def test_cannot_rent_equipment_already_in_use(client, user_token):
    # Equipment 2 is "MacBook InUse" (status=IN_USE)
    payload = {"equipment_id": 2}
    response = client.post(
        "/api/v1/rentals",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 409
    assert "Cannot rent equipment that is not Available" in response.json()["detail"]


def test_cannot_return_other_users_rental(client, admin_token, user_token):
    # 1. Admin rents Equipment 1 (iPhone Available)
    payload = {"equipment_id": 1}
    rent_response = client.post(
        "/api/v1/rentals",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert rent_response.status_code == 201
    rental_id = rent_response.json()["id"]

    # 2. Regular user tries to return Admin's rental
    return_response = client.post(
        f"/api/v1/rentals/{rental_id}/return",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert return_response.status_code == 403
    assert "Cannot return equipment rented by another user" in return_response.json()["detail"]


def test_successful_rent_changes_status_to_in_use(client, user_token):
    # Equipment 1 is "iPhone Available" (status=AVAILABLE)
    payload = {"equipment_id": 1}
    rent_response = client.post(
        "/api/v1/rentals",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert rent_response.status_code == 201

    # Verify equipment status is now "In use"
    eq_response = client.get(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert eq_response.status_code == 200
    eq_list = eq_response.json()
    eq1 = next(item for item in eq_list if item["id"] == 1)
    assert eq1["status"] == "In use"


def test_successful_return_changes_status_to_available(client, user_token):
    # 1. User rents Equipment 1
    payload = {"equipment_id": 1}
    rent_response = client.post(
        "/api/v1/rentals",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert rent_response.status_code == 201
    rental_id = rent_response.json()["id"]

    # 2. User returns Equipment 1
    return_response = client.post(
        f"/api/v1/rentals/{rental_id}/return",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert return_response.status_code == 200
    assert return_response.json()["returned_at"] is not None

    # Verify equipment status is now "Available"
    eq_response = client.get(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    eq_list = eq_response.json()
    eq1 = next(item for item in eq_list if item["id"] == 1)
    assert eq1["status"] == "Available"


def test_admin_can_return_other_users_rental(client, admin_token, user_token):
    # 1. User rents Equipment 1
    payload = {"equipment_id": 1}
    rent_response = client.post(
        "/api/v1/rentals",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert rent_response.status_code == 201
    rental_id = rent_response.json()["id"]

    # 2. Admin successfully returns User's rental
    return_response = client.post(
        f"/api/v1/rentals/{rental_id}/return",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert return_response.status_code == 200
    assert return_response.json()["returned_at"] is not None

    # Verify equipment status is now "Available"
    eq_response = client.get(
        "/api/v1/equipment",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    eq_list = eq_response.json()
    eq1 = next(item for item in eq_list if item["id"] == 1)
    assert eq1["status"] == "Available"


def test_user_sees_own_rentals_and_admin_sees_all_rentals(client, admin_token, user_token):
    # 1. Admin rents Equipment 1, then returns it
    admin_rent = client.post(
        "/api/v1/rentals",
        json={"equipment_id": 1},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_rent.status_code == 201
    admin_rental_id = admin_rent.json()["id"]
    client.post(
        f"/api/v1/rentals/{admin_rental_id}/return",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 2. Regular user rents Equipment 1, then returns it
    user_rent = client.post(
        "/api/v1/rentals",
        json={"equipment_id": 1},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert user_rent.status_code == 201
    user_rental_id = user_rent.json()["id"]
    client.post(
        f"/api/v1/rentals/{user_rental_id}/return",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # 3. GET /rentals as Admin should show all rentals in the system
    admin_list = client.get(
        "/api/v1/rentals",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_list.status_code == 200
    admin_rentals = admin_list.json()
    assert len(admin_rentals) >= 2
    rental_ids = [r["id"] for r in admin_rentals]
    assert admin_rental_id in rental_ids
    assert user_rental_id in rental_ids

    # 4. GET /rentals as User should only show User's rental
    user_list = client.get(
        "/api/v1/rentals",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert user_list.status_code == 200
    user_rentals = user_list.json()
    assert len(user_rentals) == 1
    assert user_rentals[0]["id"] == user_rental_id


def test_admin_can_toggle_repair_status(admin_client):
    # Equipment 1 is "iPhone Available" (status=AVAILABLE)
    # Admin changes status to "Repair"
    payload = {"status": "Repair"}
    response = admin_client.patch(
        "/api/v1/equipment/1",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Repair"

    # Admin changes status back to "Available"
    payload = {"status": "Available"}
    response = admin_client.patch(
        "/api/v1/equipment/1",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Available"


def test_non_admin_cannot_create_user(user_client):
    payload = {
        "username": "unauthorized_user",
        "password": "some_password",
        "is_admin": False,
    }
    response = user_client.post("/api/v1/users", json=payload)
    assert response.status_code == 403

