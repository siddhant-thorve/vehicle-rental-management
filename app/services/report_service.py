from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.branch import Branch
from app.models.vehicle import Vehicle
from app.models.booking import Booking
from app.repositories.invoice_repo import InvoiceRepository
from app.schemas.report import (
    UtilisationReportResponse,
    UtilisationBranchReport,
    RevenueReportResponse,
    RevenueCategoryReport,
)


class ReportService:
    @staticmethod
    def get_utilisation_report(db: Session, from_date: date, to_date: date) -> UtilisationReportResponse:
        branches = db.scalars(select(Branch).where(Branch.is_active.is_(True))).all()
        start_dt = datetime.combine(from_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(to_date, time.max, tzinfo=timezone.utc)
        days_in_range = max(1, (to_date - from_date).days + 1)

        branch_reports: List[UtilisationBranchReport] = []

        for b in branches:
            total_vehicles = db.scalar(
                select(func.count(Vehicle.id)).where(Vehicle.branch_id == b.id)
            ) or 0
            active_vehicles = db.scalar(
                select(func.count(Vehicle.id)).where(
                    Vehicle.branch_id == b.id,
                    Vehicle.is_active.is_(True),
                    Vehicle.status != "RETIRED",
                )
            ) or 0

            # Find all bookings overlapping the report range for this branch
            bookings = db.scalars(
                select(Booking).where(
                    Booking.branch_id == b.id,
                    Booking.status.in_(["CONFIRMED", "IN_PROGRESS", "COMPLETED"]),
                    Booking.pickup_at <= end_dt,
                    Booking.drop_at >= start_dt,
                )
            ).all()

            total_booked_seconds = 0.0
            for bk in bookings:
                # Clamp booking time to the report range
                bk_pickup = bk.pickup_at if bk.pickup_at.tzinfo else bk.pickup_at.replace(tzinfo=timezone.utc)
                bk_drop = bk.drop_at if bk.drop_at.tzinfo else bk.drop_at.replace(tzinfo=timezone.utc)
                overlap_start = max(start_dt, bk_pickup)
                overlap_end = min(end_dt, bk_drop)
                if overlap_end > overlap_start:
                    total_booked_seconds += (overlap_end - overlap_start).total_seconds()

            booked_hours = Decimal(str(round(total_booked_seconds / 3600.0, 2)))
            fleet_available_hours = Decimal(active_vehicles * days_in_range * 24)

            if fleet_available_hours > Decimal("0.00"):
                util_pct = ((booked_hours / fleet_available_hours) * Decimal("100.00")).quantize(Decimal("0.01"))
            else:
                util_pct = Decimal("0.00")

            branch_reports.append(
                UtilisationBranchReport(
                    branch_id=b.id,
                    branch_name=b.name,
                    city=b.city,
                    total_vehicles=total_vehicles,
                    active_vehicles=active_vehicles,
                    total_rentals=len(bookings),
                    total_booked_hours=booked_hours,
                    total_fleet_available_hours=fleet_available_hours,
                    utilisation_percentage=util_pct,
                )
            )

        return UtilisationReportResponse(
            start_date=from_date,
            end_date=to_date,
            branches=branch_reports,
        )

    @staticmethod
    def get_revenue_report(db: Session, from_date: date, to_date: date) -> RevenueReportResponse:
        records = InvoiceRepository.get_revenue_by_branch_and_category(db, from_date, to_date)
        breakdown: List[RevenueCategoryReport] = []
        overall_revenue = Decimal("0.00")

        for r in records:
            cat_report = RevenueCategoryReport(
                branch_id=r.branch_id,
                branch_name=r.branch_name,
                category_id=r.category_id,
                category_name=r.category_name,
                rental_count=r.rental_count,
                base_revenue=Decimal(str(r.base_revenue)),
                extra_km_revenue=Decimal(str(r.extra_km_revenue)),
                extra_hour_revenue=Decimal(str(r.extra_hour_revenue)),
                fuel_revenue=Decimal(str(r.fuel_revenue)),
                damage_revenue=Decimal(str(r.damage_revenue)),
                tax_revenue=Decimal(str(r.tax_revenue)),
                total_revenue=Decimal(str(r.total_revenue)),
            )
            overall_revenue += cat_report.total_revenue
            breakdown.append(cat_report)

        return RevenueReportResponse(
            start_date=from_date,
            end_date=to_date,
            total_revenue=overall_revenue,
            breakdown=breakdown,
        )
