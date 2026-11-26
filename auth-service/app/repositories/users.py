from collections.abc import Callable

from sqlalchemy.orm import Session

from app.models.entities import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_customer_licence(db: Session, customer: User) -> User:
    customer.licence_verified = True
    db.commit()
    db.refresh(customer)
    return customer


def seed_users_if_missing(
    db: Session, marker_email: str, create_users: Callable[[], list[User]]
) -> bool:
    if get_user_by_email(db, marker_email):
        return False

    db.add_all(create_users())
    db.commit()
    return True
