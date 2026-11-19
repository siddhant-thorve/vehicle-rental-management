from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.auth import CustomerRegisterRequest, UserResponse


def test_customer_registration_accepts_pdf_field_names() -> None:
    request = CustomerRegisterRequest(
        email="customer@example.com",
        password="secure-password",
        full_name="  Alex Customer  ",
        phone=" 555-0100 ",
        licence_no=" LIC-12345 ",
    )

    assert request.full_name == "Alex Customer"
    assert request.phone == "555-0100"
    assert request.licence_no == "LIC-12345"


def test_customer_registration_accepts_model_licence_attribute_name() -> None:
    request = CustomerRegisterRequest(
        email="customer@example.com",
        password="secure-password",
        full_name="Alex Customer",
        phone="555-0100",
        licence_number="LIC-12345",
    )

    assert request.licence_no == "LIC-12345"


def test_customer_registration_rejects_password_over_bcrypt_byte_limit() -> None:
    with pytest.raises(ValidationError):
        CustomerRegisterRequest(
            email="customer@example.com",
            password="é" * 37,
            full_name="Alex Customer",
            phone="555-0100",
            licence_no="LIC-12345",
        )


def test_user_response_does_not_expose_password_or_raw_licence() -> None:
    user = SimpleNamespace(
        id=1,
        full_name="Alex Customer",
        email="customer@example.com",
        phone="555-0100",
        licence_verified=False,
        role="CUSTOMER",
        branch_id=None,
        is_active=True,
        password_hash="not-for-response",
        licence_number="LIC-12345",
    )

    response = UserResponse.model_validate(user)

    assert "password_hash" not in response.model_dump()
    assert "licence_number" not in response.model_dump()
