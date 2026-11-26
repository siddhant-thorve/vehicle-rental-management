from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.models.entities import Booking
from app.services.pricing import calculate_cheapest_rate


def _mock_booking_services(monkeypatch, vehicle_status="AVAILABLE"):
    vehicle = {
        "id": 10,
        "branch_id": 1,
        "category_id": 2,
        "status": vehicle_status,
    }
    tariff = {
        "hourly_rate": "100",
        "daily_rate": "1000",
        "weekly_rate": "5000",
        "deposit_amount": "2000",
    }

    def fake_get(url, **kwargs):
        body = vehicle if "/vehicles/" in url else tariff
        return SimpleNamespace(status_code=200, json=lambda: body)

    monkeypatch.setattr("app.routers.bookings.httpx.get", fake_get)


def _create_booking(client, monkeypatch, pickup_offset_hours=48, duration_hours=24):
    _mock_booking_services(monkeypatch)
    pickup = datetime.now(timezone.utc) + timedelta(hours=pickup_offset_hours)
    response = client.post(
        "/bookings",
        json={
            "vehicle_id": 10,
            "branch_id": 1,
            "category_id": 2,
            "pickup_at": pickup.isoformat(),
            "drop_at": (pickup + timedelta(hours=duration_hours)).isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_req_F12_availability_search_returns_non_overlapping_vehicles(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.bookings.httpx.get",
        lambda *args, **kwargs: SimpleNamespace(
            status_code=200,
            json=lambda: [{"id": 10}, {"id": 11}],
        ),
    )
    start = datetime.now(timezone.utc) + timedelta(days=2)
    response = client.get(
        "/availability",
        params={
            "branch_id": 1,
            "category_id": 2,
            "pickup_at": start.isoformat(),
            "drop_at": (start + timedelta(hours=5)).isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json()["available_count"] == 2
    assert [vehicle["id"] for vehicle in response.json()["vehicles"]] == [10, 11]


def test_req_F13_quote_uses_cheapest_available_tariff(client, monkeypatch):
    _mock_booking_services(monkeypatch)
    start = datetime.now(timezone.utc) + timedelta(days=2)

    response = client.post(
        "/bookings/quote",
        json={
            "category_id": 2,
            "pickup_at": start.isoformat(),
            "drop_at": (start + timedelta(hours=5)).isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json()["estimated_amount"] == "500"


def test_req_F14_verified_customer_can_create_booking(client, monkeypatch):
    booking = _create_booking(client, monkeypatch)

    assert booking["customer_id"] == 1
    assert booking["status"] == "CONFIRMED"


def test_req_F15_customer_can_view_own_booking(client, monkeypatch):
    booking = _create_booking(client, monkeypatch)

    assert client.get(f"/bookings/{booking['id']}").status_code == 200
    assert client.get("/bookings/me").json()[0]["id"] == booking["id"]


def test_req_F16_customer_can_cancel_booking_and_receive_refund(client, monkeypatch):
    booking = _create_booking(client, monkeypatch, pickup_offset_hours=48)

    response = client.patch(f"/bookings/{booking['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    assert response.json()["refund_amount"] == "2000.00"


def test_req_F17_branch_staff_can_view_branch_bookings(client, monkeypatch, user_data):
    booking = _create_booking(client, monkeypatch)
    user_data.update(role="BRANCH_STAFF", branch_id=1)

    response = client.get("/bookings/branch")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [booking["id"]]


@pytest.mark.parametrize(
    ("duration_hours", "expected"),
    [(5, Decimal("500")), (48, Decimal("2000")), (240, Decimal("8000"))],
)
def test_rule_B01_pricing_uses_cheapest_hour_day_week_combination(
    duration_hours, expected
):
    amount, _ = calculate_cheapest_rate(
        hourly_rate=Decimal("100"),
        daily_rate=Decimal("1000"),
        weekly_rate=Decimal("5000"),
        duration_hours=duration_hours,
    )

    assert amount == expected


@pytest.mark.parametrize(
    ("start_offset", "duration", "expected_status"),
    [
        (2, 20, 409),
        (-3, 10, 409),
        (15, 10, 409),
        (5, 5, 409),
        (-3, 30, 409),
        (22, 5, 201),
    ],
)
def test_rule_B02_booking_prevents_overlapping_time_windows(
    client, monkeypatch, db_session, start_offset, duration, expected_status
):
    booking = _create_booking(client, monkeypatch)
    existing = db_session.query(Booking).filter_by(id=booking["id"]).one()
    original_start = existing.pickup_at
    existing.pickup_at = original_start + timedelta(hours=2)
    existing.drop_at = existing.pickup_at + timedelta(hours=20)
    db_session.commit()
    _mock_booking_services(monkeypatch)

    response = client.post(
        "/bookings",
        json={
            "vehicle_id": 10,
            "branch_id": 1,
            "category_id": 2,
            "pickup_at": (original_start + timedelta(hours=start_offset)).isoformat(),
            "drop_at": (
                original_start + timedelta(hours=start_offset + duration)
            ).isoformat(),
        },
    )

    assert response.status_code == expected_status


def test_rule_B03_booking_rejects_unverified_customer(client, monkeypatch, user_data):
    user_data["licence_verified"] = False
    _mock_booking_services(monkeypatch)
    pickup = datetime.now(timezone.utc) + timedelta(days=2)

    response = client.post(
        "/bookings",
        json={
            "vehicle_id": 10,
            "branch_id": 1,
            "category_id": 2,
            "pickup_at": pickup.isoformat(),
            "drop_at": (pickup + timedelta(hours=5)).isoformat(),
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("pickup_offset_hours", "duration_hours"),
    [(-1, 5), (48, 3)],
)
def test_rule_B07_pickup_must_be_future_and_rental_at_least_four_hours(
    client, monkeypatch, pickup_offset_hours, duration_hours
):
    _mock_booking_services(monkeypatch)
    pickup = datetime.now(timezone.utc) + timedelta(hours=pickup_offset_hours)

    response = client.post(
        "/bookings",
        json={
            "vehicle_id": 10,
            "branch_id": 1,
            "category_id": 2,
            "pickup_at": pickup.isoformat(),
            "drop_at": (pickup + timedelta(hours=duration_hours)).isoformat(),
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("pickup_offset_hours", "expected_refund"),
    [(48, "2000.00"), (12, "1000.00"), (-1, "0.00")],
)
def test_rule_B08_cancellation_refund_depends_on_pickup_time(
    client, monkeypatch, db_session, pickup_offset_hours, expected_refund
):
    booking = _create_booking(client, monkeypatch, pickup_offset_hours=48)
    row = db_session.query(Booking).filter_by(id=booking["id"]).one()
    row.pickup_at = datetime.now(timezone.utc) + timedelta(hours=pickup_offset_hours)
    db_session.commit()

    response = client.patch(f"/bookings/{booking['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["refund_amount"] == expected_refund


def test_rule_B09_unavailable_vehicle_cannot_be_booked(client, monkeypatch):
    _mock_booking_services(monkeypatch, vehicle_status="UNDER_MAINTENANCE")
    pickup = datetime.now(timezone.utc) + timedelta(days=2)

    response = client.post(
        "/bookings",
        json={
            "vehicle_id": 10,
            "branch_id": 1,
            "category_id": 2,
            "pickup_at": pickup.isoformat(),
            "drop_at": (pickup + timedelta(hours=5)).isoformat(),
        },
    )

    assert response.status_code == 400


def test_rule_B10_branch_staff_cannot_view_another_branch_booking(
    client, monkeypatch, user_data
):
    booking = _create_booking(client, monkeypatch)
    user_data.update(role="BRANCH_STAFF", branch_id=2)

    response = client.get(f"/bookings/{booking['id']}")

    assert response.status_code == 403
