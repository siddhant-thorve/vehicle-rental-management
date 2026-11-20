from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.rental import Rental


class RentalRepository:
    @staticmethod
    def get_by_id(db: Session, rental_id: int) -> Optional[Rental]:
        return db.get(Rental, rental_id)

    @staticmethod
    def get_by_booking_id(db: Session, booking_id: int) -> Optional[Rental]:
        stmt = select(Rental).where(Rental.booking_id == booking_id)
        return db.scalars(stmt).first()

    @staticmethod
    def create(db: Session, rental: Rental) -> Rental:
        db.add(rental)
        db.commit()
        db.refresh(rental)
        return rental

    @staticmethod
    def update(db: Session, rental: Rental) -> Rental:
        db.commit()
        db.refresh(rental)
        return rental
