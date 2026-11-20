from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.branch import Branch
from app.schemas.branch import BranchCreate
from app.repositories.branch_repo import BranchRepository

logger = logging.getLogger("branch_audit")


class BranchService:
    @staticmethod
    def create_branch(db: Session, req: BranchCreate) -> Branch:
        branch = Branch(
            name=req.name,
            city=req.city,
            address=req.address,
            contact_no=req.contact_no,
            is_active=True,
        )
        created = BranchRepository.create(db, branch)
        logger.info(f"AUDIT: Branch created with ID {created.id}")
        return created

    @staticmethod
    def list_branches(
        db: Session,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> Tuple[List[Branch], int]:
        skip = (page - 1) * size
        return BranchRepository.list_branches(
            db=db,
            city=city,
            is_active=is_active,
            skip=skip,
            limit=size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
