import pytest
from types import SimpleNamespace
from pydantic import ValidationError
from app.schemas.auth import CustomerRegisterRequest, UserResponse

def test_customer_registration_accepts_pdf_field_names():
    r = CustomerRegisterRequest(email="c@e.com", password="secure-password", full_name=" Alex ", phone=" 555-0100 ", licence_no=" LIC-12345 ")
    assert r.full_name == "Alex" and r.phone == "555-0100" and r.licence_no == "LIC-12345"

def test_customer_registration_accepts_model_licence_attribute_name():
    assert CustomerRegisterRequest(email="c@e.com", password="secure-password", full_name="A", phone="555", licence_number="LIC-1").licence_no == "LIC-1"

def test_customer_registration_rejects_password_over_bcrypt_byte_limit():
    with pytest.raises(ValidationError):
        CustomerRegisterRequest(email="c@e.com", password="é" * 37, full_name="A", phone="555", licence_no="L")

def test_user_response_does_not_expose_password_or_raw_licence():
    u = SimpleNamespace(id=1, full_name="A", email="c@e.com", phone="555", licence_verified=False, role="CUSTOMER", branch_id=None, is_active=True, password_hash="h", licence_number="L")
    d = UserResponse.model_validate(u).model_dump()
    assert "password_hash" not in d and "licence_number" not in d





