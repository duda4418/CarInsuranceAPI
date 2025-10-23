from db.models import Owner, Car
import pytest

# Helper to create an owner (since owner endpoints not shown)

def create_owner(db_session, name="Alice", email="alice@example.com"):
    owner = Owner(name=name, email=email)
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    return owner


def test_create_car_success(client, db_session):
    owner = create_owner(db_session)
    payload = {
        "vin": "VIN123",
        "make": "Ford",
        "model": "Focus",
        "year_of_manufacture": 2022,
        "owner_id": owner.id
    }
    resp = client.post("/api/cars", json=payload)
    assert resp.status_code == 201
    assert "Location" in resp.headers
    data = resp.json()
    assert data["vin"] == payload["vin"]
    assert data["owner"]["id"] == owner.id


def test_create_car_duplicate_vin(client, db_session):
    owner = create_owner(db_session)
    payload = {
        "vin": "VIN_DUP",
        "make": "Ford",
        "model": "Fiesta",
        "year_of_manufacture": 2021,
        "owner_id": owner.id
    }
    first = client.post("/api/cars", json=payload)
    assert first.status_code == 201
    second = client.post("/api/cars", json=payload)
    # Domain validation error -> expect 400 mapped via exception handler
    assert second.status_code == 400


def test_get_car_not_found(client):
    resp = client.get("/api/cars/99999")
    assert resp.status_code == 404


def test_update_car_success(client, db_session):
    owner = create_owner(db_session)
    payload = {
        "vin": "VINUPD1",
        "make": "Ford",
        "model": "Focus",
        "year_of_manufacture": 2022,
        "owner_id": owner.id
    }
    create_resp = client.post("/api/cars", json=payload)
    car_id = create_resp.json()["id"]

    update_payload = {
        "vin": "VINUPD2",  # change vin
        "make": "Ford",
        "model": "Fusion",
        "year_of_manufacture": 2023,
        "owner_id": owner.id
    }
    upd = client.put(f"/api/cars/{car_id}", json=update_payload)
    assert upd.status_code == 200
    data = upd.json()
    assert data["vin"] == "VINUPD2"
    assert data["model"] == "Fusion"


def test_update_car_vin_duplicate(client, db_session):
    owner = create_owner(db_session)
    # Create first car
    payload_a = {"vin": "VIN_A", "make": "A", "model": "M1", "year_of_manufacture": 2020, "owner_id": owner.id}
    car_a = client.post("/api/cars", json=payload_a).json()
    payload_b = {"vin": "VIN_B", "make": "B", "model": "M2", "year_of_manufacture": 2021, "owner_id": owner.id}
    car_b = client.post("/api/cars", json=payload_b).json()

    # Attempt to update car_b to use VIN_A
    update_payload = {**payload_b, "vin": "VIN_A"}
    resp = client.put(f"/api/cars/{car_b['id']}", json=update_payload)
    assert resp.status_code == 400


def test_delete_car_success(client, db_session):
    owner = create_owner(db_session)
    payload = {"vin": "VINDEL", "make": "Ford", "model": "Edge", "year_of_manufacture": 2021, "owner_id": owner.id}
    create_resp = client.post("/api/cars", json=payload)
    car_id = create_resp.json()["id"]
    del_resp = client.delete(f"/api/cars/{car_id}")
    assert del_resp.status_code == 204
    # Subsequent get -> 404
    get_resp = client.get(f"/api/cars/{car_id}")
    assert get_resp.status_code == 404


def test_delete_car_not_found(client):
    resp = client.delete("/api/cars/54321")
    assert resp.status_code == 404
