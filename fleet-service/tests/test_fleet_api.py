from types import SimpleNamespace


def test_create_and_update_branch(client):
    created = client.post(
        "/branches",
        json={
            "name": "Central Branch",
            "city": "Mumbai",
            "address": "1 Main Street",
            "contact_no": "1234567890",
        },
    )

    assert created.status_code == 201
    branch_id = created.json()["id"]
    assert client.get(f"/branches/{branch_id}").status_code == 200

    updated = client.patch(
        f"/branches/{branch_id}",
        json={"address": "2 Main Street"},
    )
    assert updated.status_code == 200
    assert updated.json()["address"] == "2 Main Street"


def test_register_vehicle_checks_catalog(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.fleet.httpx.get",
        lambda *args, **kwargs: SimpleNamespace(
            status_code=200, raise_for_status=lambda: None
        ),
    )
    branch = client.post(
        "/branches",
        json={
            "name": "Central Branch",
            "city": "Mumbai",
            "address": "1 Main Street",
            "contact_no": "1234567890",
        },
    ).json()

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
    assert response.json()["category_id"] == 1
