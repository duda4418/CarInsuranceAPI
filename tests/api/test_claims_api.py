from fastapi.testclient import TestClient
from tests.utils.factories import create_car


def test_create_claim_success(client, db_session):
    car = create_car(db_session, make="VW", model="Golf")

    payload = {
        "car_id": car.id,
        "description": "Rear bumper scratch",
        "amount": 250.75,
        "claim_date": "2025-02-01"
    }
    resp = client.post("/api/claims", json=payload)
    assert resp.status_code == 201
    assert "Location" in resp.headers
    data = resp.json()
    assert data["description"] == payload["description"]
    assert float(data["amount"]) == payload["amount"]


def test_create_claim_car_not_found(client):
    payload = {
        "car_id": 9999,
        "description": "Bad",
        "amount": 10,
        "claim_date": "2025-02-02"
    }
    resp = client.post("/api/claims", json=payload)
    assert resp.status_code == 404


def test_get_claim_not_found(client):
    resp = client.get("/api/claims/9999")
    assert resp.status_code == 404
