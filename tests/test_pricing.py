from decimal import Decimal
from app.services.pricing_service import PricingService


def test_cheapest_rate_5_hours():
    # Acceptance Criteria: Cheapest-rate pricing is covered by unit tests for 5 hours
    hourly = Decimal("100.00")
    daily = Decimal("1500.00")
    weekly = Decimal("7000.00")

    cost, breakdown = PricingService.calculate_cheapest_rate(
        hourly_rate=hourly,
        daily_rate=daily,
        weekly_rate=weekly,
        duration_hours=5,
    )
    # 5 * 100 = 500 (< 1500)
    assert cost == Decimal("500.00")
    assert breakdown["hours"] == 5
    assert breakdown["days"] == 0
    assert breakdown["weeks"] == 0


def test_cheapest_rate_2_days():
    # Acceptance Criteria: Cheapest-rate pricing is covered by unit tests for 2 days (48 hours)
    hourly = Decimal("100.00")
    daily = Decimal("1500.00")
    weekly = Decimal("7000.00")

    cost, breakdown = PricingService.calculate_cheapest_rate(
        hourly_rate=hourly,
        daily_rate=daily,
        weekly_rate=weekly,
        duration_hours=48,
    )
    # 2 days * 1500 = 3000 (< 48 * 100 = 4800, and < 7000)
    assert cost == Decimal("3000.00")
    assert breakdown["days"] == 2
    assert breakdown["weeks"] == 0
    assert breakdown["hours"] == 0


def test_cheapest_rate_10_days():
    # Acceptance Criteria: Cheapest-rate pricing is covered by unit tests for 10 days (240 hours)
    hourly = Decimal("100.00")
    daily = Decimal("1500.00")
    weekly = Decimal("7000.00")

    cost, breakdown = PricingService.calculate_cheapest_rate(
        hourly_rate=hourly,
        daily_rate=daily,
        weekly_rate=weekly,
        duration_hours=240,
    )
    # 1 week (7000) + 3 days (3 * 1500 = 4500) = 11500 (< 10 * 1500 = 15000, < 2 weeks = 14000)
    assert cost == Decimal("11500.00")
    assert breakdown["weeks"] == 1
    assert breakdown["days"] == 3
    assert breakdown["hours"] == 0


def test_tariff_endpoint_rejects_negative_or_zero_amounts(client, seed_test_data, admin_headers):
    # Security requirement: Tariff endpoints must reject negative or zero amounts
    cat_id = seed_test_data["category"].id
    invalid_tariff = {
        "category_id": cat_id,
        "hourly_rate": -10.0,
        "daily_rate": 1000.0,
        "weekly_rate": 5000.0,
        "free_km_per_day": 100.0,
        "extra_km_rate": 10.0,
        "extra_hour_rate": 100.0,
        "deposit_amount": 2000.0,
    }
    resp = client.post("/tariffs", json=invalid_tariff, headers=admin_headers)
    assert resp.status_code == 422 or resp.status_code == 400
