import pytest
from app.models.equipment import EquipmentStatus


def test_list_equipment_unauthorized(client):
    response = client.get("/api/v1/equipment")
    assert response.status_code == 401


def test_list_equipment_success(user_client):
    response = user_client.get("/api/v1/equipment")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    # Check that keys are serialized correctly
    for item in data:
        assert "id" in item
        assert "name" in item
        assert "brand" in item
        assert "status" in item


def test_list_equipment_filter_status(user_client):
    response = user_client.get("/api/v1/equipment?status=Available")
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "Available" for item in data)


def test_list_equipment_filter_brand(user_client):
    response = user_client.get("/api/v1/equipment?brand=Razer")
    assert response.status_code == 200
    data = response.json()
    assert all(item["brand"] == "Razer" for item in data)


def test_list_equipment_sorting(user_client):
    response = user_client.get("/api/v1/equipment?sort_by=name&order=desc")
    assert response.status_code == 200
    data = response.json()
    names = [item["name"] for item in data]
    assert names == sorted(names, reverse=True)


def test_create_equipment_non_admin(user_client):
    payload = {
        "name": "Sony Headphones",
        "brand": "Sony",
        "purchase_date": "2023-01-10",
        "status": "Available",
    }
    response = user_client.post("/api/v1/equipment", json=payload)
    assert response.status_code == 403


def test_create_equipment_success(admin_client):
    payload = {
        "name": "Sony Headphones",
        "brand": "Sony",
        "purchase_date": "2023-01-10",
        "status": "Available",
    }
    response = admin_client.post("/api/v1/equipment", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sony Headphones"
    assert data["brand"] == "Sony"
    assert data["purchase_date"] == "2023-01-10"
    assert data["status"] == "Available"


def test_patch_equipment_non_admin(user_client):
    payload = {"name": "Updated iPhone"}
    response = user_client.patch("/api/v1/equipment/1", json=payload)
    assert response.status_code == 403


def test_patch_equipment_success(admin_client):
    payload = {"name": "Updated Name", "status": "Repair"}
    response = admin_client.patch("/api/v1/equipment/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "Repair"


def test_patch_equipment_status_repair_when_in_use_fails(admin_client):
    # Equipment 2 is "InUse" in conftest.py
    payload = {"status": "Repair"}
    response = admin_client.patch("/api/v1/equipment/2", json=payload)
    assert response.status_code == 409
    assert "Cannot set status to Repair on equipment that is In use" in response.json()["detail"]


def test_delete_equipment_non_admin(user_client):
    response = user_client.delete("/api/v1/equipment/1")
    assert response.status_code == 403


def test_delete_equipment_in_use_fails(admin_client):
    # Equipment 2 is "InUse" in conftest.py
    response = admin_client.delete("/api/v1/equipment/2")
    assert response.status_code == 409
    assert "Cannot delete equipment that is currently In use" in response.json()["detail"]


def test_delete_equipment_success(admin_client):
    # Equipment 1 is "Available"
    response = admin_client.delete("/api/v1/equipment/1")
    assert response.status_code == 204

    # Verify it is deleted
    get_resp = admin_client.get("/api/v1/equipment")
    assert not any(item["id"] == 1 for item in get_resp.json())


def test_patch_equipment_status_available_when_in_use_fails(admin_client):
    payload = {"status": "Available"}
    response = admin_client.patch("/api/v1/equipment/2", json=payload)
    assert response.status_code == 409
    assert "Cannot change status on equipment that is In use. It must be returned first." in response.json()["detail"]


def test_patch_equipment_status_to_in_use_fails(admin_client):
    payload = {"status": "In use"}
    response = admin_client.patch("/api/v1/equipment/1", json=payload)
    assert response.status_code == 409
    assert "Cannot manually set status to In use." in response.json()["detail"]


def test_delete_equipment_with_active_rental_and_available_status_fails(client, admin_token, db_session):
    from app.models.rental import Rental
    from datetime import datetime, timezone
    # 1. Create a rental directly in DB, leaving returned_at as None, but keep equipment status as Available
    rental = Rental(equipment_id=1, user_id=2, rented_at=datetime.now(timezone.utc))
    db_session.add(rental)
    db_session.commit()

    # 2. Attempt to delete equipment 1
    response = client.delete(
        "/api/v1/equipment/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409
    assert "Cannot delete equipment that has an active rental" in response.json()["detail"]
