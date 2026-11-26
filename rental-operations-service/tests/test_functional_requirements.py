from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

from app.models.entities import Invoice, Rental
from app.schemas.api import ReturnRequest
from app.services.operations import calculate_invoice


def _booking(status="CONFIRMED"):
    pickup = datetime.now(timezone.utc) - timedelta(hours=1)
    return SimpleNamespace(
        id=22,
        customer_id=1,
        vehicle_id=9,
        branch_id=1,
        status=status,
        pickup_at=pickup,
        drop_at=datetime.now(timezone.utc) + timedelta(hours=1),
        estimated_amount=Decimal("100.00"),
        deposit_amount=Decimal("50.00"),
    )


def _invoice(rental_id=1):
    return Invoice(
        id=1,
        rental_id=rental_id,
        base_amount=Decimal("100.00"),
        extra_km_amount=Decimal("10.00"),
        extra_hour_amount=Decimal("5.00"),
        fuel_charge=Decimal("0.00"),
        damage_charge=Decimal("0.00"),
        tax_amount=Decimal("20.70"),
        total_amount=Decimal("135.70"),
        deposit_adjusted=Decimal("50.00"),
        payable_amount=Decimal("85.70"),
        generated_at=datetime.now(timezone.utc),
    )


def test_req_F18_staff_records_pickup_and_starts_rental(client, monkeypatch):
    monkeypatch.setattr("app.routers.operations.fetch_booking", lambda _: _booking())
    rental = Rental(
        id=1,
        booking_id=22,
        actual_pickup_at=datetime.now(timezone.utc),
        odometer_out=Decimal("100"),
        fuel_out=Decimal("80"),
    )
    monkeypatch.setattr("app.routers.operations.record_pickup", lambda *args: rental)

    response = client.post(
        "/rentals/22/pickup",
        json={"odometer_out": 100, "fuel_out": 80},
    )

    assert response.status_code == 201
    assert response.json()["booking_id"] == 22
    assert response.json()["odometer_out"] == "100"


def test_req_F19_staff_records_return_and_generates_invoice(
    client, monkeypatch, db_session
):
    rental = Rental(
        booking_id=22,
        actual_pickup_at=datetime.now(timezone.utc) - timedelta(hours=2),
        odometer_out=Decimal("100"),
        fuel_out=Decimal("80"),
    )
    db_session.add(rental)
    db_session.commit()
    monkeypatch.setattr(
        "app.routers.operations.fetch_booking", lambda _: _booking("IN_PROGRESS")
    )
    invoice = _invoice(rental.id)
    monkeypatch.setattr(
        "app.routers.operations.record_return", lambda *args: invoice
    )

    response = client.post(
        "/rentals/22/return",
        json={"odometer_in": 150, "fuel_in": 80},
    )

    assert response.status_code == 200
    assert response.json()["rental_id"] == rental.id
    assert response.json()["payable_amount"] == "85.70"


def test_req_F20_invoice_calculates_mileage_late_and_tax_charges():
    pickup = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    booking = SimpleNamespace(
        estimated_amount=Decimal("100.00"),
        deposit_amount=Decimal("50.00"),
        drop_at=pickup + timedelta(hours=24),
    )
    rental = SimpleNamespace(id=1, actual_pickup_at=pickup, odometer_out=Decimal("0"))
    request = ReturnRequest(
        odometer_in=Decimal("250"),
        fuel_in=Decimal("80"),
        fuel_charge=Decimal("10"),
        damage_charge=Decimal("0"),
    )

    invoice = calculate_invoice(
        booking,
        rental,
        request,
        {"free_km_per_day": 100, "extra_km_rate": 2, "extra_hour_rate": 50},
        pickup + timedelta(hours=26),
    )

    assert invoice.extra_km_amount == Decimal("100.00")
    assert invoice.extra_hour_amount == Decimal("100.00")
    assert invoice.total_amount == Decimal("365.80")


def test_req_F21_customer_can_retrieve_own_invoice(
    client, monkeypatch, db_session
):
    rental = Rental(
        booking_id=22,
        actual_pickup_at=datetime.now(timezone.utc),
        odometer_out=Decimal("100"),
        fuel_out=Decimal("80"),
    )
    db_session.add(rental)
    db_session.flush()
    invoice = _invoice(rental.id)
    db_session.add(invoice)
    db_session.commit()
    monkeypatch.setattr("app.routers.operations.fetch_booking", lambda _: _booking())

    response = client.get(f"/invoices/{rental.id}")

    assert response.status_code == 200
    assert response.json()["rental_id"] == rental.id


def test_req_F22_admin_gets_fleet_utilisation_report(
    client, monkeypatch, user_data
):
    user_data["role"] = "ADMIN"

    def fake_get(url, **kwargs):
        body = (
            [{"id": 1, "name": "Central", "city": "Mumbai"}]
            if "/branches" in url
            else [{"id": 9, "status": "AVAILABLE"}]
        )
        return SimpleNamespace(json=lambda: body, raise_for_status=lambda: None)

    monkeypatch.setattr("app.routers.operations.httpx.get", fake_get)
    monkeypatch.setattr(
        "app.routers.operations.list_report_bookings",
        lambda *args: [
            {
                "pickup_at": "2026-01-01T10:00:00+00:00",
                "drop_at": "2026-01-01T14:00:00+00:00",
            }
        ],
    )

    response = client.get("/reports/utilisation")

    assert response.status_code == 200
    assert response.json()["branches"][0]["total_booked_hours"] == 4
    assert response.json()["branches"][0]["utilisation_percentage"] > 0


def test_req_F23_admin_gets_revenue_totals(client, db_session, user_data):
    user_data["role"] = "ADMIN"
    db_session.add(
        Rental(
            id=1,
            booking_id=22,
            actual_pickup_at=datetime.now(timezone.utc),
            odometer_out=Decimal("100"),
            fuel_out=Decimal("80"),
        )
    )
    db_session.flush()
    db_session.add(_invoice(rental_id=1))
    db_session.commit()

    response = client.get("/reports/revenue")

    assert response.status_code == 200
    assert response.json()["invoice_count"] == 1
    assert response.json()["total_revenue"] == 135.7


def test_rule_B04_return_rejects_decreased_odometer(
    client, monkeypatch, db_session
):
    rental = Rental(
        booking_id=22,
        actual_pickup_at=datetime.now(timezone.utc),
        odometer_out=Decimal("100"),
        fuel_out=Decimal("80"),
    )
    db_session.add(rental)
    db_session.commit()
    monkeypatch.setattr(
        "app.routers.operations.fetch_booking", lambda _: _booking("IN_PROGRESS")
    )

    response = client.post(
        "/rentals/22/return",
        json={"odometer_in": 99, "fuel_in": 80},
    )

    assert response.status_code == 400


def test_rule_B05_pickup_requires_confirmed_booking(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.operations.fetch_booking", lambda _: _booking("CANCELLED")
    )

    response = client.post(
        "/rentals/22/pickup",
        json={"odometer_out": 100, "fuel_out": 80},
    )

    assert response.status_code == 400


def test_rule_B06_return_requires_in_progress_booking(client, monkeypatch):
    monkeypatch.setattr("app.routers.operations.fetch_booking", lambda _: _booking())

    response = client.post(
        "/rentals/22/return",
        json={"odometer_in": 100, "fuel_in": 80},
    )

    assert response.status_code == 400
