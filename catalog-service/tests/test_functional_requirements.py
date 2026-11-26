def test_req_F06_admin_manages_vehicle_categories(client):
    response = client.post(
        "/vehicle-categories",
        json={
            "name": "Family SUV",
            "description": "Seven seats",
            "seating_capacity": 7,
        },
    )

    assert response.status_code == 201
    assert client.get(f"/vehicle-categories/{response.json()['id']}").status_code == 200


def test_req_F10_admin_defines_category_tariff(client):
    category = client.post(
        "/vehicle-categories",
        json={"name": "Economy", "seating_capacity": 4},
    ).json()
    response = client.post(
        "/tariffs",
        json={
            "category_id": category["id"],
            "hourly_rate": 100,
            "daily_rate": 1000,
            "weekly_rate": 5000,
            "free_km_per_day": 100,
            "extra_km_rate": 10,
            "extra_hour_rate": 50,
            "deposit_amount": 2000,
        },
    )

    assert response.status_code == 201
    assert response.json()["category_id"] == category["id"]


def test_req_F11_tariff_includes_extra_kilometre_and_hour_rates(client):
    category = client.post(
        "/vehicle-categories",
        json={"name": "Premium", "seating_capacity": 5},
    ).json()
    response = client.post(
        "/tariffs",
        json={
            "category_id": category["id"],
            "hourly_rate": 100,
            "daily_rate": 1000,
            "weekly_rate": 5000,
            "free_km_per_day": 100,
            "extra_km_rate": 12,
            "extra_hour_rate": 75,
            "deposit_amount": 2000,
        },
    )

    assert response.status_code == 201
    assert response.json()["extra_km_rate"] == "12.00"
    assert response.json()["extra_hour_rate"] == "75.00"
