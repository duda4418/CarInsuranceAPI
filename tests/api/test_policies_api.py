from fastapi.testclient import TestClient
from tests.utils.factories import create_car


def test_create_policy_success(client, db_session):
    # Arrange: create a car with VIN + owner
    car = create_car(db_session, make="Ford", model="Fiesta")

    payload = {
        "car_id": car.id,
        "provider": "Acme Insurance",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }

    # Act
    resp = client.post("/api/policies", json=payload)

    # Assert
    assert resp.status_code == 201
    assert "Location" in resp.headers
    data = resp.json()
    assert data["provider"] == payload["provider"]
    assert data["endDate"] == payload["end_date"]


def test_get_policy_not_found(client):
    resp = client.get("/api/policies/99999")
    assert resp.status_code == 404
