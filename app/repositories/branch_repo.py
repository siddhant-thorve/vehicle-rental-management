from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, asc
from app.models.branch import Branch


class BranchRepository:
    @staticmethod
    def get_by_id(db: Session, branch_id: int) -> Optional[Branch]:
        return db.get(Branch, branch_id)

    @staticmethod
    def create(db: Session, branch: Branch) -> Branch:
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch

    @staticmethod
    def list_branches(
        db: Session,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[List[Branch], int]:
        stmt = select(Branch)
        count_stmt = select(func.count(Branch.id))

        if city:
            stmt = stmt.where(Branch.city.ilike(f"%{city}%"))
            count_stmt = count_stmt.where(Branch.city.ilike(f"%{city}%"))
        if is_active is not None:
            stmt = stmt.where(Branch.is_active == is_active)
            count_stmt = count_stmt.where(Branch.is_active == is_active)

        sort_col = getattr(Branch, sort_by, Branch.id)
        if sort_dir.lower() == "desc":
            stmt = stmt.order_by(desc(sort_col))
        else:
            stmt = stmt.order_by(asc(sort_col))

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.offset(skip).limit(limit)).all())
        return items, total
