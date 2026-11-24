from datetime import UTC, datetime
from types import SimpleNamespace
from app.schemas.branch import BranchCreate, BranchResponse, BranchUpdate

def test_branch_create_accepts_fields_and_contact_number():
    b = BranchCreate(name=" Central ", city=" Pune ", address=" 1 Main Street ", contact_no=" 555-0100 ")
    assert b.name == " Central " and b.city == " Pune " and b.address == " 1 Main Street " and b.contact_no == " 555-0100 "

def test_branch_update_allows_partial_or_empty_update():
    assert BranchUpdate().model_dump(exclude_none=True) == {} and BranchUpdate(name="Central").name == "Central"

def test_branch_response_requires_contact_number():
    now = datetime.now(UTC)
    b = SimpleNamespace(id=1, name="Central", city="Pune", address="1 Main Street", contact_no="555-0100", is_active=True, created_at=now, updated_at=now)
    assert BranchResponse.model_validate(b).contact_no == "555-0100"
