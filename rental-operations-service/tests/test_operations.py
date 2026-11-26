from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from app.schemas.api import ReturnRequest
from app.services.operations import calculate_invoice


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "rental-operations-service"


def test_invoice_calculation_uses_rental_and_tariff_data():
    booking = SimpleNamespace(
        estimated_amount=Decimal("100.00"),
        deposit_amount=Decimal("50.00"),
        drop_at=datetime(2026, 1, 2, 10, tzinfo=timezone.utc),
    )
    rental = SimpleNamespace(
        id=1,
        actual_pickup_at=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
        odometer_out=Decimal("100.00"),
    )
    request = ReturnRequest(
        odometer_in=Decimal("150.00"),
        fuel_in=Decimal("80"),
        fuel_charge=Decimal("10.00"),
        damage_charge=Decimal("0.00"),
    )
    tariff = {
        "free_km_per_day": 200,
        "extra_km_rate": 10,
        "extra_hour_rate": 50,
    }

    invoice = calculate_invoice(
        booking,
        rental,
        request,
        tariff,
        datetime(2026, 1, 2, 10, tzinfo=timezone.utc),
    )

    assert invoice.total_amount == Decimal("129.80")
    assert invoice.deposit_adjusted == Decimal("50.00")
    assert invoice.payable_amount == Decimal("79.80")
