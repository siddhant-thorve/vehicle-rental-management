from datetime import datetime, timezone, timedelta
from decimal import Decimal


def test_quote_endpoint(client, seed_test_data, customer_headers):
    # User story 13: As a customer, view computed estimated rental amount
    now = datetime.now(timezone.utc)
    cat_id = seed_test_data["category"].id
    payload = {
        "category_id": cat_id,
        "pickup_at": (now + timedelta(days=1)).isoformat(),
        "drop_at": (now + timedelta(days=1, hours=5)).isoformat(),
    }
    resp = client.post("/bookings/quote", json=payload, headers=customer_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["duration_hours"] == 5
    assert Decimal(str(data["estimated_amount"])) == Decimal("500.00")
    assert Decimal(str(data["deposit_amount"])) == Decimal("3000.00")


def test_unverified_customer_cannot_book(client, seed_test_data, unverified_headers):
    # Business Rule 4: Only customers with licence_verified = true may create a booking
    now = datetime.now(timezone.utc)
    veh1_id = seed_test_data["veh1"].id
    payload = {
        "vehicle_id": veh1_id,
        "pickup_at": (now + timedelta(days=2)).isoformat(),
        "drop_at": (now + timedelta(days=2, hours=6)).isoformat(),
    }
    resp = client.post("/bookings", json=payload, headers=unverified_headers)
    assert resp.status_code == 400
    assert "not verified" in resp.json()["detail"].lower()


def test_booking_minimum_duration_violation(client, seed_test_data, customer_headers):
    # Business Rule 2: Minimum rental duration is 4 hours
    now = datetime.now(timezone.utc)
    veh1_id = seed_test_data["veh1"].id
    payload = {
        "vehicle_id": veh1_id,
        "pickup_at": (now + timedelta(days=2)).isoformat(),
        "drop_at": (now + timedelta(days=2, hours=2)).isoformat(),  # only 2 hours!
    }
    resp = client.post("/bookings", json=payload, headers=customer_headers)
    assert resp.status_code == 400
    assert "4 hours" in resp.json()["detail"]


def test_overlapping_booking_rejections(client, seed_test_data, customer_headers):
    """
    Acceptance Criteria:
    Overlapping-booking rejection is proven by tests covering:
    - partial overlap at both ends (start and end)
    - full containment (both inner and outer)
    - exact match
    """
    now = datetime.now(timezone.utc)
    veh1_id = seed_test_data["veh1"].id

    # Base booking: [now + 10 days, now + 12 days]
    t_start = now + timedelta(days=10)
    t_end = now + timedelta(days=12)

    base_resp = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": t_start.isoformat(),
            "drop_at": t_end.isoformat(),
        },
        headers=customer_headers,
    )
    assert base_resp.status_code == 201

    # 1. Partial overlap at start (starts before, ends inside: [t_start - 1d, t_start + 1d])
    resp_start = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": (t_start - timedelta(days=1)).isoformat(),
            "drop_at": (t_start + timedelta(days=1)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp_start.status_code == 409
    assert resp_start.json()["code"] == "CONFLICT"

    # 2. Partial overlap at end (starts inside, ends after: [t_end - 1d, t_end + 1d])
    resp_end = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": (t_end - timedelta(days=1)).isoformat(),
            "drop_at": (t_end + timedelta(days=1)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp_end.status_code == 409
    assert resp_end.json()["code"] == "CONFLICT"

    # 3. Full containment - Outer (starts before, ends after: [t_start - 1d, t_end + 1d])
    resp_outer = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": (t_start - timedelta(days=1)).isoformat(),
            "drop_at": (t_end + timedelta(days=1)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp_outer.status_code == 409
    assert resp_outer.json()["code"] == "CONFLICT"

    # 4. Full containment - Inner (starts inside, ends inside: [t_start + 4h, t_end - 4h])
    resp_inner = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": (t_start + timedelta(hours=4)).isoformat(),
            "drop_at": (t_end - timedelta(hours=4)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp_inner.status_code == 409
    assert resp_inner.json()["code"] == "CONFLICT"

    # 5. Exact match ([t_start, t_end])
    resp_exact = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": t_start.isoformat(),
            "drop_at": t_end.isoformat(),
        },
        headers=customer_headers,
    )
    assert resp_exact.status_code == 409
    assert resp_exact.json()["code"] == "CONFLICT"


def test_cancellation_policy(client, seed_test_data, customer_headers):
    # Business Rule 5: Cancellation policy
    now = datetime.now(timezone.utc)
    veh1_id = seed_test_data["veh1"].id

    # 1. More than 24 hours prior to pickup -> full refund (rental + deposit)
    t_pickup_far = now + timedelta(days=5)
    t_drop_far = t_pickup_far + timedelta(days=2)
    resp = client.post(
        "/bookings",
        json={"vehicle_id": veh1_id, "pickup_at": t_pickup_far.isoformat(), "drop_at": t_drop_far.isoformat()},
        headers=customer_headers,
    )
    assert resp.status_code == 201
    bk_id = resp.json()["id"]

    cancel_resp = client.patch(f"/bookings/{bk_id}/cancel", headers=customer_headers)
    assert cancel_resp.status_code == 200
    cancel_data = cancel_resp.json()
    assert cancel_data["status"] == "CANCELLED"
    # Full refund = 3000 (2 days @ 1500) + 3000 (deposit) = 6000
    assert Decimal(str(cancel_data["refund_amount"])) == Decimal("6000.00")


def test_customer_idor_check_on_booking(client, seed_test_data, customer_headers, unverified_headers):
    # Security requirement: Customer A cannot read Customer B's booking
    now = datetime.now(timezone.utc)
    veh2_id = seed_test_data["veh2"].id
    # Create booking for Customer 1
    resp = client.post(
        "/bookings",
        json={
            "vehicle_id": veh2_id,
            "pickup_at": (now + timedelta(days=20)).isoformat(),
            "drop_at": (now + timedelta(days=21)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp.status_code == 201
    bk_id = resp.json()["id"]

    # Customer 2 attempts to read Customer 1's booking
    read_resp = client.get(f"/bookings/{bk_id}", headers=unverified_headers)
    assert read_resp.status_code == 403
    assert read_resp.json()["code"] == "FORBIDDEN"
