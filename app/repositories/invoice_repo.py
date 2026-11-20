from datetime import date, datetime, time
from typing import Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from app.models.invoice import Invoice
from app.models.rental import Rental
from app.models.booking import Booking
from app.models.vehicle import Vehicle, VehicleCategory
from app.models.branch import Branch


class InvoiceRepository:
    @staticmethod
    def get_by_id(db: Session, invoice_id: int) -> Optional[Invoice]:
        return db.get(Invoice, invoice_id)

    @staticmethod
    def get_by_rental_id(db: Session, rental_id: int) -> Optional[Invoice]:
        stmt = select(Invoice).where(Invoice.rental_id == rental_id)
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, invoice: Invoice) -> Invoice:
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def get_revenue_by_branch_and_category(
        db: Session,
        from_date: date,
        to_date: date,
    ) -> List[Any]:
        start_dt = datetime.combine(from_date, time.min)
        end_dt = datetime.combine(to_date, time.max)

        stmt = (
            select(
                Branch.id.label("branch_id"),
                Branch.name.label("branch_name"),
                VehicleCategory.id.label("category_id"),
                VehicleCategory.name.label("category_name"),
                func.count(Invoice.id).label("rental_count"),
                func.coalesce(func.sum(Invoice.base_amount), 0).label("base_revenue"),
                func.coalesce(func.sum(Invoice.extra_km_amount), 0).label("extra_km_revenue"),
                func.coalesce(func.sum(Invoice.extra_hour_amount), 0).label("extra_hour_revenue"),
                func.coalesce(func.sum(Invoice.fuel_charge), 0).label("fuel_revenue"),
                func.coalesce(func.sum(Invoice.damage_charge), 0).label("damage_revenue"),
                func.coalesce(func.sum(Invoice.tax_amount), 0).label("tax_revenue"),
                func.coalesce(func.sum(Invoice.total_amount), 0).label("total_revenue"),
            )
            .join(Rental, Invoice.rental_id == Rental.id)
            .join(Booking, Rental.booking_id == Booking.id)
            .join(Branch, Booking.branch_id == Branch.id)
            .join(Vehicle, Booking.vehicle_id == Vehicle.id)
            .join(VehicleCategory, Vehicle.category_id == VehicleCategory.id)
            .where(Invoice.generated_at >= start_dt, Invoice.generated_at <= end_dt)
            .group_by(Branch.id, Branch.name, VehicleCategory.id, VehicleCategory.name)
            .order_by(Branch.name, VehicleCategory.name)
        )
        return db.execute(stmt).all()
