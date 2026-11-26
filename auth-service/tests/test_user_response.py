from types import SimpleNamespace

from app.schemas.api import UserResponse


def test_licence_number_is_masked_in_response_without_mutating_source():
    source = SimpleNamespace(
        id=1,
        email="customer@example.com",
        full_name="Test Customer",
        phone="1234567890",
        licence_no="MH0120200012345",
        licence_verified=True,
        role="CUSTOMER",
        branch_id=None,
        is_active=True,
    )

    response = UserResponse.model_validate(source)

    assert response.licence_no == "MH0120200012345"
    assert response.model_dump()["licence_no"] == "MH****2345"
    assert source.licence_no == "MH0120200012345"


def test_short_licence_number_is_fully_masked():
    source = SimpleNamespace(
        id=1,
        email="customer@example.com",
        full_name="Test Customer",
        phone="1234567890",
        licence_no="AB12",
        licence_verified=True,
        role="CUSTOMER",
        branch_id=None,
        is_active=True,
    )

    response = UserResponse.model_validate(source)

    assert response.model_dump()["licence_no"] == "****"


def test_missing_licence_number_stays_none():
    source = SimpleNamespace(
        id=1,
        email="staff@example.com",
        full_name="Test Staff",
        phone="1234567890",
        licence_no=None,
        licence_verified=True,
        role="BRANCH_STAFF",
        branch_id=1,
        is_active=True,
    )

    response = UserResponse.model_validate(source)

    assert response.model_dump()["licence_no"] is None
