from datetime import datetime, timezone, timedelta
from decimal import Decimal

def test_branch_staff_cannot_act_on_another_branch_booking(client, seed_test_data, customer_headers, staff2_headers):
    now, vid = datetime.now(timezone.utc), seed_test_data["veh1"].id
    bk = client.post("/bookings", json={"vehicle_id": vid, "pickup_at": (now + timedelta(days=1)).isoformat(), "drop_at": (now + timedelta(days=2)).isoformat()}, headers=customer_headers).json()
    r = client.post(f"/rentals/{bk['id']}/pickup", json={"odometer_out": 10000.0, "fuel_out": 100.0}, headers=staff2_headers)
    assert r.status_code == 403 and r.json()["code"] == "FORBIDDEN" and "another branch" in r.json()["detail"].lower()

def test_rental_lifecycle_pickup_return_and_settlement(client, seed_test_data, customer_headers, staff1_headers):
    now, vid = datetime.now(timezone.utc), seed_test_data["veh1"].id
    bk = client.post("/bookings", json={"vehicle_id": vid, "pickup_at": (now + timedelta(days=3)).isoformat(), "drop_at": (now + timedelta(days=4)).isoformat()}, headers=customer_headers).json()
    r_pick = client.post(f"/rentals/{bk['id']}/pickup", json={"odometer_out": 10000.0, "fuel_out": 100.0}, headers=staff1_headers)
    assert r_pick.status_code == 201 and any(v["id"] == vid and v["status"] == "BOOKED" for v in client.get("/vehicles?branch_id=1").json()["items"])
    rental_id = r_pick.json()["id"]
    bad_ret = client.post(f"/rentals/{bk['id']}/return", json={"odometer_in": 9999.0, "fuel_in": 90.0, "damage_notes": None, "fuel_charge": 0.0, "damage_charge": 0.0}, headers=staff1_headers)
    assert bad_ret.status_code == 400 and "odometer_in" in bad_ret.json()["detail"]
    ret = client.post(f"/rentals/{bk['id']}/return", json={"odometer_in": 10250.0, "fuel_in": 100.0, "damage_notes": "All good", "fuel_charge": 0.0, "damage_charge": 0.0}, headers=staff1_headers)
    assert ret.status_code == 200
    inv = ret.json()
    assert Decimal(str(inv["extra_km_amount"])) == Decimal("1000.00") and Decimal(str(inv["total_amount"])) == Decimal("2950.00") and Decimal(str(inv["payable_amount"])) == Decimal("0.00")
    assert client.get(f"/invoices/{rental_id}", headers=customer_headers).status_code == 200 and client.get(f"/invoices/{rental_id}", headers=customer_headers).json()["id"] == inv["id"]
