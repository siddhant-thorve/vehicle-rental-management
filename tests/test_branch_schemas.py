from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.branch import BranchCreate, BranchResponse, BranchUpdate


def test_branch_create_strips_fields_and_accepts_contact_number() -> None:
    branch = BranchCreate(
        name="  Central  ",
        city=" Pune ",
        address=" 1 Main Street ",
        contact_no=" 555-0100 ",
    )

    assert branch.name == "Central"
    assert branch.city == "Pune"
    assert branch.address == "1 Main Street"
    assert branch.contact_no == "555-0100"


def test_branch_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError):
        BranchUpdate()


def test_branch_response_supports_existing_model_without_contact_number() -> None:
    now = datetime.now(UTC)
    branch = SimpleNamespace(
        id=1,
        name="Central",
        city="Pune",
        address="1 Main Street",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    response = BranchResponse.model_validate(branch)

    assert response.contact_no is None
