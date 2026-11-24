from decimal import Decimal
from app.services.pricing_service import PricingService

R = (Decimal("100.00"), Decimal("1500.00"), Decimal("7000.00"))

def test_cheapest_rate_5_hours():
    c, b = PricingService.calculate_cheapest_rate(*R, duration_hours=5)
    assert c == Decimal("500.00") and b["hours"] == 5 and b["days"] == 0 and b["weeks"] == 0

def test_cheapest_rate_2_days():
    c, b = PricingService.calculate_cheapest_rate(*R, duration_hours=48)
    assert c == Decimal("3000.00") and b["days"] == 2 and b["weeks"] == 0 and b["hours"] == 0

def test_cheapest_rate_10_days():
    c, b = PricingService.calculate_cheapest_rate(*R, duration_hours=240)
    assert c == Decimal("11500.00") and b["weeks"] == 1 and b["days"] == 3 and b["hours"] == 0

def test_tariff_endpoint_rejects_negative_or_zero_amounts(client, seed_test_data, admin_headers):
    p = {"category_id": seed_test_data["category"].id, "hourly_rate": -10.0, "daily_rate": 1000.0, "weekly_rate": 5000.0, "free_km_per_day": 100.0, "extra_km_rate": 10.0, "extra_hour_rate": 100.0, "deposit_amount": 2000.0}
    assert client.post("/tariffs", json=p, headers=admin_headers).status_code in (400, 422)
