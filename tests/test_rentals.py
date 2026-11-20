from datetime import datetime, timezone, timedelta
from decimal import Decimal


def test_branch_staff_cannot_act_on_another_branch_booking(client, seed_test_data, customer_headers, staff2_headers):
    """
    Acceptance Criteria:
    A branch-staff account cannot act on another branch's booking — covered by a test.
    """
    now = datetime.now(timezone.utc)
    # veh1 belongs to Branch 1 (Mumbai)
    veh1_id = seed_test_data["veh1"].id

    # Customer books vehicle in Branch 1
    resp = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": (now + timedelta(days=1)).isoformat(),
            "drop_at": (now + timedelta(days=2)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp.status_code == 201
    bk_id = resp.json()["id"]

    # Staff 2 (Delhi Branch) attempts to record pickup for Branch 1 booking
    pickup_payload = {
        "odometer_out": 10000.0,
        "fuel_out": 100.0,
    }
    pickup_resp = client.post(f"/rentals/{bk_id}/pickup", json=pickup_payload, headers=staff2_headers)
    assert pickup_resp.status_code == 403
    assert pickup_resp.json()["code"] == "FORBIDDEN"
    assert "another branch" in pickup_resp.json()["detail"].lower()


def test_rental_lifecycle_pickup_return_and_settlement(
    client, seed_test_data, customer_headers, staff1_headers
):
    now = datetime.now(timezone.utc)
    veh1_id = seed_test_data["veh1"].id

    # 1. Create booking in Branch 1
    resp = client.post(
        "/bookings",
        json={
            "vehicle_id": veh1_id,
            "pickup_at": (now + timedelta(days=3)).isoformat(),
            "drop_at": (now + timedelta(days=4)).isoformat(),
        },
        headers=customer_headers,
    )
    assert resp.status_code == 201
    bk_id = resp.json()["id"]

    # 2. Staff 1 records pickup
    pickup_payload = {
        "odometer_out": 10000.0,
        "fuel_out": 100.0,
    }
    pickup_resp = client.post(f"/rentals/{bk_id}/pickup", json=pickup_payload, headers=staff1_headers)
    assert pickup_resp.status_code == 201
    rental_id = pickup_resp.json()["id"]

    # Verify vehicle status is BOOKED (Business Rule 9)
    veh_resp = client.get("/vehicles?branch_id=1")
    assert any(v["id"] == veh1_id and v["status"] == "BOOKED" for v in veh_resp.json()["items"])

    # 3. Odometer validation failure: odometer_in < odometer_out (Business Rule 7)
    invalid_return = {
        "odometer_in": 9999.0,  # less than 10000.0!
        "fuel_in": 90.0,
        "damage_notes": None,
        "fuel_charge": 0.0,
        "damage_charge": 0.0,
    }
    fail_ret_resp = client.post(f"/rentals/{bk_id}/return", json=invalid_return, headers=staff1_headers)
    assert fail_ret_resp.status_code == 400
    assert "odometer_in" in fail_ret_resp.json()["detail"]

    # 4. Valid Return with extra km
    # Free km per day = 150 km. Let's drive 250 km (100 extra km @ 10/km = 1000 extra km charge)
    valid_return = {
        "odometer_in": 10250.0,
        "fuel_in": 100.0,
        "damage_notes": "All good",
        "fuel_charge": 0.0,
        "damage_charge": 0.0,
    }
    ret_resp = client.post(f"/rentals/{bk_id}/return", json=valid_return, headers=staff1_headers)
    assert ret_resp.status_code == 200
    invoice = ret_resp.json()

    assert Decimal(str(invoice["extra_km_amount"])) == Decimal("1000.00")
    # Base = 1500, Extra km = 1000, Subtotal = 2500, Tax 18% = 450, Total = 2950
    assert Decimal(str(invoice["total_amount"])) == Decimal("2950.00")
    # Deposit was 3000 -> Deposit adjusted = 2950 -> Payable = 0.00
    assert Decimal(str(invoice["payable_amount"])) == Decimal("0.00")

    # 5. Customer views invoice
    inv_resp = client.get(f"/invoices/{rental_id}", headers=customer_headers)
    assert inv_resp.status_code == 200
    assert inv_resp.json()["id"] == invoice["id"]
