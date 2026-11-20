from datetime import datetime, timezone, timedelta


def test_create_category_and_list(client, seed_test_data, admin_headers):
    # User story 6: maintain vehicle categories
    cat_payload = {
        "name": "SUV",
        "description": "Large SUV",
        "seating_capacity": 7,
    }
    resp = client.post("/vehicle-categories", json=cat_payload, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "SUV"

    list_resp = client.get("/vehicle-categories")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1


def test_add_vehicle_by_admin(client, seed_test_data, admin_headers):
    # User story 7: add vehicles with registration, category, branch, fuel type, odometer
    payload = {
        "registration_no": "MH-02-CD-5555",
        "category_id": seed_test_data["category"].id,
        "branch_id": seed_test_data["b1"].id,
        "make": "Toyota",
        "model": "Innova",
        "fuel_type": "Diesel",
        "transmission": "Automatic",
        "odometer_km": 15000.0,
    }
    resp = client.post("/vehicles", json=payload, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["registration_no"] == "MH-02-CD-5555"
    assert data["status"] == "AVAILABLE"


def test_list_and_filter_vehicles_with_pagination(client, seed_test_data):
    # User story 9: list and filter fleet by branch, category and status with pagination
    b1_id = seed_test_data["b1"].id
    resp = client.get(f"/vehicles?branch_id={b1_id}&status=AVAILABLE&page=1&size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(v["branch_id"] == b1_id for v in data["items"])


def test_mark_vehicle_under_maintenance_by_branch_staff(client, seed_test_data, staff1_headers):
    # User story 8: mark vehicle as UNDER_MAINTENANCE so that it is excluded from search
    veh1_id = seed_test_data["veh1"].id
    resp = client.patch(f"/vehicles/{veh1_id}/status", json={"status": "UNDER_MAINTENANCE"}, headers=staff1_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "UNDER_MAINTENANCE"

    # Verify search excludes UNDER_MAINTENANCE
    now = datetime.now(timezone.utc)
    pickup = (now + timedelta(days=2)).isoformat()
    drop = (now + timedelta(days=2, hours=10)).isoformat()
    b1_id = seed_test_data["b1"].id
    search_resp = client.get(
        "/availability",
        params={"branch_id": b1_id, "pickup_at": pickup, "drop_at": drop},
    )
    assert search_resp.status_code == 200
    assert not any(v["id"] == veh1_id for v in search_resp.json())


def test_branch_staff_cross_branch_vehicle_status_rejected(client, seed_test_data, staff2_headers):
    # Security requirement: Branch staff 2 cannot modify Branch 1 vehicle
    veh1_id = seed_test_data["veh1"].id
    resp = client.patch(f"/vehicles/{veh1_id}/status", json={"status": "UNDER_MAINTENANCE"}, headers=staff2_headers)
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"
