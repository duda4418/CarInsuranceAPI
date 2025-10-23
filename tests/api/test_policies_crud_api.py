from tests.utils.factories import create_car


def test_update_policy_success(client, db_session):
    car = create_car(db_session, vin="VPOLX1")
    payload = {
        "car_id": car.id,
        "provider": "ProviderA",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    create_resp = client.post("/api/policies", json=payload)
    policy_id = create_resp.json()["id"]

    update_payload = {
        "car_id": car.id,
        "provider": "ProviderB",
        "start_date": "2025-02-01",
        "end_date": "2025-12-31"
    }
    upd = client.put(f"/api/policies/{policy_id}", json=update_payload)
    assert upd.status_code == 200
    assert upd.json()["provider"] == "ProviderB"
    # camelCase key in response
    assert upd.json()["startDate"] == "2025-02-01"


def test_update_policy_reassign_car(client, db_session):
    car1 = create_car(db_session, vin="VPOLA1")
    car2 = create_car(db_session, vin="VPOLB2")
    payload = {
        "car_id": car1.id,
        "provider": "ProviderA",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    create_resp = client.post("/api/policies", json=payload)
    policy_id = create_resp.json()["id"]

    update_payload = {
        "car_id": car2.id,
        "provider": "ProviderA",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    upd = client.put(f"/api/policies/{policy_id}", json=update_payload)
    assert upd.status_code == 200
    # camelCase key in response
    assert upd.json()["carId"] == car2.id


def test_update_policy_reassign_car_not_found(client, db_session):
    car = create_car(db_session, vin="VPOLNF1")
    payload = {
        "car_id": car.id,
        "provider": "ProviderA",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    create_resp = client.post("/api/policies", json=payload)
    policy_id = create_resp.json()["id"]

    update_payload = {
        "car_id": 99999,
        "provider": "ProviderA",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    upd = client.put(f"/api/policies/{policy_id}", json=update_payload)
    assert upd.status_code == 404


def test_delete_policy_success(client, db_session):
    car = create_car(db_session, vin="VPOLD1")
    payload = {
        "car_id": car.id,
        "provider": "ProviderA",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    create_resp = client.post("/api/policies", json=payload)
    policy_id = create_resp.json()["id"]
    del_resp = client.delete(f"/api/policies/{policy_id}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/api/policies/{policy_id}")
    assert get_resp.status_code == 404


def test_delete_policy_not_found(client):
    resp = client.delete("/api/policies/777777")
    assert resp.status_code == 404
