import math
from decimal import Decimal
from typing import Dict, Any, Tuple


class PricingService:
    @staticmethod
    def calculate_cheapest_rate(
        hourly_rate: Decimal,
        daily_rate: Decimal,
        weekly_rate: Decimal,
        duration_hours: int,
    ) -> Tuple[Decimal, Dict[str, Any]]:
        """
        Finds the cheapest valid combination of weekly, daily, and hourly rates
        that covers at least `duration_hours`.
        Returns:
            Tuple of (total_cost, breakdown_dict)
        """
        if duration_hours <= 0:
            return Decimal("0.00"), {"weeks": 0, "days": 0, "hours": 0}

        best_cost = None
        best_breakdown = None

        max_weeks = math.ceil(duration_hours / 168) + 1

        for w in range(max_weeks + 1):
            for d in range(9):  # 0 to 8 days
                for h in range(25):  # 0 to 24 hours
                    hours_covered = w * 168 + d * 24 + h
                    if hours_covered >= duration_hours:
                        cost = (
                            Decimal(w) * weekly_rate
                            + Decimal(d) * daily_rate
                            + Decimal(h) * hourly_rate
                        )
                        if best_cost is None or cost < best_cost:
                            best_cost = cost
                            best_breakdown = {
                                "weeks": w,
                                "days": d,
                                "hours": h,
                                "hours_covered": hours_covered,
                                "duration_requested": duration_hours,
                            }

        return best_cost or Decimal("0.00"), best_breakdown or {}
