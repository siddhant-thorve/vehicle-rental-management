from datetime import datetime, timezone, timedelta
from decimal import Decimal

def test_quote_endpoint(client, seed_test_data, customer_headers):
    now = datetime.now(timezone.utc)
    p = {"category_id": seed_test_data["category"].id, "pickup_at": (now + timedelta(days=1)).isoformat(), "drop_at": (now + timedelta(days=1, hours=5)).isoformat()}
    r = client.post("/bookings/quote", json=p, headers=customer_headers)
    assert r.status_code == 200 and r.json()["duration_hours"] == 5 and Decimal(str(r.json()["estimated_amount"])) == Decimal("500.00") and Decimal(str(r.json()["deposit_amount"])) == Decimal("3000.00")

def test_unverified_customer_cannot_book(client, seed_test_data, unverified_headers):
    now = datetime.now(timezone.utc)
    p = {"vehicle_id": seed_test_data["veh1"].id, "pickup_at": (now + timedelta(days=2)).isoformat(), "drop_at": (now + timedelta(days=2, hours=6)).isoformat()}
    r = client.post("/bookings", json=p, headers=unverified_headers)
    assert r.status_code == 400 and "not verified" in r.json()["detail"].lower()

def test_booking_minimum_duration_violation(client, seed_test_data, customer_headers):
    now = datetime.now(timezone.utc)
    p = {"vehicle_id": seed_test_data["veh1"].id, "pickup_at": (now + timedelta(days=2)).isoformat(), "drop_at": (now + timedelta(days=2, hours=2)).isoformat()}
    r = client.post("/bookings", json=p, headers=customer_headers)
    assert r.status_code == 400 and "4 hours" in r.json()["detail"]

def test_overlapping_booking_rejections(client, seed_test_data, customer_headers):
    now, vid = datetime.now(timezone.utc), seed_test_data["veh1"].id
    t1, t2 = now + timedelta(days=10), now + timedelta(days=12)
    assert client.post("/bookings", json={"vehicle_id": vid, "pickup_at": t1.isoformat(), "drop_at": t2.isoformat()}, headers=customer_headers).status_code == 201
    for p, d in [
        (t1 - timedelta(days=1), t1 + timedelta(days=1)),
        (t2 - timedelta(days=1), t2 + timedelta(days=1)),
        (t1 - timedelta(days=1), t2 + timedelta(days=1)),
        (t1 + timedelta(hours=4), t2 - timedelta(hours=4)),
        (t1, t2),
    ]:
        r = client.post("/bookings", json={"vehicle_id": vid, "pickup_at": p.isoformat(), "drop_at": d.isoformat()}, headers=customer_headers)
        assert r.status_code == 409 and r.json()["code"] == "CONFLICT"

def test_cancellation_policy(client, seed_test_data, customer_headers):
    now, vid = seed_test_data["veh1"].id, seed_test_data["veh1"].id
    now = datetime.now(timezone.utc)
    t1, t2 = now + timedelta(days=5), now + timedelta(days=7)
    bk = client.post("/bookings", json={"vehicle_id": vid, "pickup_at": t1.isoformat(), "drop_at": t2.isoformat()}, headers=customer_headers).json()
    r = client.patch(f"/bookings/{bk['id']}/cancel", headers=customer_headers)
    assert r.status_code == 200 and r.json()["status"] == "CANCELLED" and Decimal(str(r.json()["refund_amount"])) == Decimal("6000.00")

def test_customer_idor_check_on_booking(client, seed_test_data, customer_headers, unverified_headers):
    now, vid = datetime.now(timezone.utc), seed_test_data["veh2"].id
    bk = client.post("/bookings", json={"vehicle_id": vid, "pickup_at": (now + timedelta(days=20)).isoformat(), "drop_at": (now + timedelta(days=21)).isoformat()}, headers=customer_headers).json()
    r = client.get(f"/bookings/{bk['id']}", headers=unverified_headers)
    assert r.status_code == 403 and r.json()["code"] == "FORBIDDEN"
