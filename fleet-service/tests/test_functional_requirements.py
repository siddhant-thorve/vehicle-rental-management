from types import SimpleNamespace


def _create_branch(client):
    response = client.post(
        "/branches",
        json={
            "name": "Central Branch",
            "city": "Mumbai",
            "address": "1 Main Street",
            "contact_no": "1234567890",
        },
    )
    assert response.status_code == 201
    return response.json()


def _mock_catalog(monkeypatch, status_code=200):
    monkeypatch.setattr(
        "app.routers.fleet.httpx.get",
        lambda *args, **kwargs: SimpleNamespace(
            status_code=status_code,
            raise_for_status=lambda: None,
        ),
    )


def test_req_F05_admin_creates_and_updates_branch(client):
    branch = _create_branch(client)
    updated = client.patch(
        f"/branches/{branch['id']}", json={"address": "2 Main Street"}
    )

    assert updated.status_code == 200
    assert updated.json()["address"] == "2 Main Street"


def test_req_F07_admin_registers_vehicle(client, monkeypatch):
    _mock_catalog(monkeypatch)
    branch = _create_branch(client)
    response = client.post(
        "/vehicles",
        json={
            "registration_no": "MH-01-AB-1001",
            "category_id": 1,
            "branch_id": branch["id"],
            "make": "Example",
            "model": "Car",
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "odometer_km": 10,
        },
    )

    assert response.status_code == 201
    assert response.json()["registration_no"] == "MH-01-AB-1001"


def test_req_F08_staff_marks_vehicle_for_maintenance(client, monkeypatch, user_data):
    _mock_catalog(monkeypatch)
    branch = _create_branch(client)
    vehicle = client.post(
        "/vehicles",
        json={
            "registration_no": "MH-01-AB-1002",
            "category_id": 1,
            "branch_id": branch["id"],
            "make": "Example",
            "model": "Car",
            "fuel_type": "Petrol",
            "transmission": "Manual",
        },
    ).json()
    user_data.update(role="BRANCH_STAFF", branch_id=branch["id"])

    response = client.patch(
        f"/vehicles/{vehicle['id']}/status",
        json={"status": "UNDER_MAINTENANCE"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_MAINTENANCE"


def test_req_F09_fleet_can_be_filtered_and_paginated(client, monkeypatch):
    _mock_catalog(monkeypatch)
    branch = _create_branch(client)
    for registration in ("MH-01-AB-1003", "MH-01-AB-1004"):
        client.post(
            "/vehicles",
            json={
                "registration_no": registration,
                "category_id": 1,
                "branch_id": branch["id"],
                "make": "Example",
                "model": "Car",
                "fuel_type": "Petrol",
                "transmission": "Manual",
            },
        )

    response = client.get(
        "/vehicles",
        params={"branch_id": branch["id"], "category_id": 1, "page": 1, "size": 1},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
