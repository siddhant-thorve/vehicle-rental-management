from datetime import date
from decimal import Decimal
from typing import List
from pydantic import BaseModel


class UtilisationBranchReport(BaseModel):
    branch_id: int
    branch_name: str
    city: str
    total_vehicles: int
    active_vehicles: int
    total_rentals: int
    total_booked_hours: Decimal
    total_fleet_available_hours: Decimal
    utilisation_percentage: Decimal


class UtilisationReportResponse(BaseModel):
    start_date: date
    end_date: date
    branches: List[UtilisationBranchReport]


class RevenueCategoryReport(BaseModel):
    branch_id: int
    branch_name: str
    category_id: int
    category_name: str
    rental_count: int
    base_revenue: Decimal
    extra_km_revenue: Decimal
    extra_hour_revenue: Decimal
    fuel_revenue: Decimal
    damage_revenue: Decimal
    tax_revenue: Decimal
    total_revenue: Decimal


class RevenueReportResponse(BaseModel):
    start_date: date
    end_date: date
    total_revenue: Decimal
    breakdown: List[RevenueCategoryReport]
