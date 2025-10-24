from tests.utils.factories import create_car


def test_update_claim_success(client, db_session):
    car = create_car(db_session, vin="VNCLM2")
    payload = {
        "car_id": car.id,
        "description": "Scratch",
        "amount": 100.0,
        "claim_date": "2025-02-01"
    }
    create_resp = client.post("/api/claims", json=payload)
    claim_id = create_resp.json()["id"]

    update_payload = {
        "car_id": car.id,
        "description": "Scratch repainted",
        "amount": 180.0,
        "claim_date": "2025-02-05"
    }
    upd = client.put(f"/api/claims/{claim_id}", json=update_payload)
    assert upd.status_code == 200
    data = upd.json()
    assert data["description"] == "Scratch repainted"
    assert float(data["amount"]) == 180.0



def test_update_claim_car_id_immutable(client, db_session):
    car1 = create_car(db_session, vin="VNCLMA")
    car2 = create_car(db_session, vin="VNCLMB")
    payload = {
        "car_id": car1.id,
        "description": "Broken light",
        "amount": 60.0,
        "claim_date": "2025-03-01"
    }
    create_resp = client.post("/api/claims", json=payload)
    claim_id = create_resp.json()["id"]

    update_payload = {
        "car_id": car2.id,  # Should be ignored
        "description": "Broken light",
        "amount": 60.0,
        "claim_date": "2025-03-01"
    }
    upd = client.put(f"/api/claims/{claim_id}", json=update_payload)
    assert upd.status_code == 200
    # carId should remain unchanged
    assert upd.json()["carId"] == car1.id



def test_update_claim_car_id_immutable_not_found(client, db_session):
    car = create_car(db_session, vin="VNCLMNF")
    payload = {
        "car_id": car.id,
        "description": "Door dent",
        "amount": 220.0,
        "claim_date": "2025-04-01"
    }
    create_resp = client.post("/api/claims", json=payload)
    claim_id = create_resp.json()["id"]

    update_payload = {
        "car_id": 999999,  # Should be ignored
        "description": "Door dent",
        "amount": 220.0,
        "claim_date": "2025-04-01"
    }
    upd = client.put(f"/api/claims/{claim_id}", json=update_payload)
    assert upd.status_code == 200
    # carId should remain unchanged
    assert upd.json()["carId"] == car.id


def test_delete_claim_success(client, db_session):
    car = create_car(db_session, vin="VNCLMD")
    payload = {
        "car_id": car.id,
        "description": "Rear bumper",
        "amount": 300.0,
        "claim_date": "2025-05-01"
    }
    create_resp = client.post("/api/claims", json=payload)
    claim_id = create_resp.json()["id"]
    del_resp = client.delete(f"/api/claims/{claim_id}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/api/claims/{claim_id}")
    assert get_resp.status_code == 404


def test_delete_claim_not_found(client):
    resp = client.delete("/api/claims/555555")
    assert resp.status_code == 404
