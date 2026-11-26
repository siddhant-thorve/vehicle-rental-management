from types import SimpleNamespace


def test_quote_uses_catalog_tariff(client, monkeypatch):
    tariff = {
        "hourly_rate": 100,
        "daily_rate": 1000,
        "weekly_rate": 5000,
        "deposit_amount": 2000,
    }
    monkeypatch.setattr(
        "app.routers.bookings.httpx.get",
        lambda *args, **kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: tariff,
        ),
    )

    response = client.post(
        "/bookings/quote",
        json={
            "category_id": 1,
            "pickup_at": "2026-11-27T10:00:00+05:30",
            "drop_at": "2026-11-27T15:00:00+05:30",
        },
    )

    assert response.status_code == 200
    assert response.json()["deposit_amount"] == "2000"


def test_quote_rejects_rentals_under_four_hours(client):
    response = client.post(
        "/bookings/quote",
        json={
            "category_id": 1,
            "pickup_at": "2026-11-27T10:00:00+05:30",
            "drop_at": "2026-11-27T12:00:00+05:30",
        },
    )

    assert response.status_code == 400
