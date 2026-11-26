def test_create_category_and_tariff(client):
    category = client.post(
        "/vehicle-categories",
        json={
            "name": "Compact",
            "description": "Small city vehicle",
            "seating_capacity": 4,
        },
    )

    assert category.status_code == 201
    category_id = category.json()["id"]

    tariff = client.post(
        "/tariffs",
        json={
            "category_id": category_id,
            "hourly_rate": 100,
            "daily_rate": 1000,
            "weekly_rate": 5000,
            "free_km_per_day": 100,
            "extra_km_rate": 10,
            "extra_hour_rate": 50,
            "deposit_amount": 2000,
        },
    )

    assert tariff.status_code == 201
    assert (
        client.get(f"/tariffs/category/{category_id}").json()["daily_rate"]
        == "1000.00"
    )


def test_tariff_requires_existing_category(client):
    response = client.post(
        "/tariffs",
        json={
            "category_id": 999,
            "hourly_rate": 100,
            "daily_rate": 1000,
            "weekly_rate": 5000,
            "free_km_per_day": 100,
            "extra_km_rate": 10,
            "extra_hour_rate": 50,
            "deposit_amount": 2000,
        },
    )

    assert response.status_code == 404
