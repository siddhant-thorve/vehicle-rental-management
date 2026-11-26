from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.entities import Invoice, Rental


def get_rental_for_booking(db: Session, booking_id: int) -> Rental | None:
    return db.query(Rental).filter(Rental.booking_id == booking_id).first()


def create_rental(db: Session, rental: Rental) -> Rental:
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


def get_rental(db: Session, rental_id: int) -> Rental | None:
    return db.query(Rental).filter(Rental.id == rental_id).first()


def complete_rental(
    db: Session,
    rental: Rental,
    invoice: Invoice,
    returned_at: datetime,
    odometer_in: Decimal,
    fuel_in: Decimal,
    damage_notes: str | None,
) -> Invoice:
    rental.actual_drop_at = returned_at
    rental.odometer_in = odometer_in
    rental.fuel_in = fuel_in
    rental.damage_notes = damage_notes
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoice(db: Session, rental_id: int) -> Invoice | None:
    return db.query(Invoice).filter(Invoice.rental_id == rental_id).first()


def list_invoices(db: Session, start_at: datetime, end_at: datetime) -> list[Invoice]:
    return (
        db.query(Invoice)
        .filter(Invoice.generated_at >= start_at, Invoice.generated_at <= end_at)
        .all()
    )
