from datetime import datetime, timezone, timedelta

def test_create_category_and_list(client, seed_test_data, admin_headers):
    r = client.post("/vehicle-categories", json={"name": "SUV", "description": "Large SUV", "seating_capacity": 7}, headers=admin_headers)
    assert r.status_code == 201 and r.json()["name"] == "SUV" and client.get("/vehicle-categories").status_code == 200 and client.get("/vehicle-categories").json()["total"] >= 1

def test_add_vehicle_by_admin(client, seed_test_data, admin_headers):
    p = {"registration_no": "MH-02-CD-5555", "category_id": seed_test_data["category"].id, "branch_id": seed_test_data["b1"].id, "make": "Toyota", "model": "Innova", "fuel_type": "Diesel", "transmission": "Automatic", "odometer_km": 15000.0}
    r = client.post("/vehicles", json=p, headers=admin_headers)
    assert r.status_code == 201 and r.json()["registration_no"] == "MH-02-CD-5555" and r.json()["status"] == "AVAILABLE"

def test_list_and_filter_vehicles_with_pagination(client, seed_test_data):
    b1_id = seed_test_data["b1"].id
    r = client.get(f"/vehicles?branch_id={b1_id}&status=AVAILABLE&page=1&size=10")
    assert r.status_code == 200 and r.json()["total"] >= 1 and all(v["branch_id"] == b1_id for v in r.json()["items"])

def test_mark_vehicle_under_maintenance_by_branch_staff(client, seed_test_data, staff1_headers):
    vid, bid = seed_test_data["veh1"].id, seed_test_data["b1"].id
    r = client.patch(f"/vehicles/{vid}/status", json={"status": "UNDER_MAINTENANCE"}, headers=staff1_headers)
    assert r.status_code == 200 and r.json()["status"] == "UNDER_MAINTENANCE"
    now = datetime.now(timezone.utc)
    s = client.get("/availability", params={"branch_id": bid, "pickup_at": (now + timedelta(days=2)).isoformat(), "drop_at": (now + timedelta(days=2, hours=10)).isoformat()})
    assert s.status_code == 200 and not any(v["id"] == vid for v in s.json())

def test_branch_staff_cross_branch_vehicle_status_rejected(client, seed_test_data, staff2_headers):
    r = client.patch(f"/vehicles/{seed_test_data['veh1'].id}/status", json={"status": "UNDER_MAINTENANCE"}, headers=staff2_headers)
    assert r.status_code == 403 and r.json()["code"] == "FORBIDDEN"

def test_availability_excludes_vehicle_with_overlapping_booking(client, seed_test_data, customer_headers):
    now = datetime.now(timezone.utc)
    pickup_at = now + timedelta(days=5)
    drop_at = pickup_at + timedelta(hours=5)
    booking = client.post(
        "/bookings",
        json={
            "vehicle_id": seed_test_data["veh1"].id,
            "pickup_at": pickup_at.isoformat(),
            "drop_at": drop_at.isoformat(),
        },
        headers=customer_headers,
    )
    assert booking.status_code == 201

    response = client.get(
        "/availability",
        params={
            "branch_id": seed_test_data["b1"].id,
            "pickup_at": pickup_at.isoformat(),
            "drop_at": drop_at.isoformat(),
            "category_id": seed_test_data["category"].id,
        },
    )
    assert response.status_code == 200
    assert all(vehicle["id"] != seed_test_data["veh1"].id for vehicle in response.json())
