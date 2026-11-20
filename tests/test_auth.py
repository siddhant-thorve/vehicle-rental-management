def test_customer_registration_success(client, seed_test_data):
    payload = {
        "email": "newuser@test.com",
        "password": "Password@123",
        "full_name": "New Customer",
        "phone": "9998887770",
        "licence_no": "KA012022001122",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "CUSTOMER"
    assert data["licence_verified"] is False


def test_customer_registration_duplicate_email(client, seed_test_data):
    payload = {
        "email": "verified@test.com",
        "password": "Password@123",
        "full_name": "Duplicate User",
        "phone": "9998887771",
        "licence_no": "KA012022001123",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"


def test_login_success(client, seed_test_data):
    payload = {
        "email": "admin@test.com",
        "password": "AdminPass123",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"
    assert data["token_type"] == "bearer"


def test_authentication_failure_wrong_password(client, seed_test_data):
    # Mandatory requirement: one authentication failure test
    payload = {
        "email": "admin@test.com",
        "password": "WrongPassword!",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_create_staff_by_admin(client, seed_test_data, admin_headers):
    # User story 3: As an admin, create branch-staff linked to a branch
    b1_id = seed_test_data["b1"].id
    payload = {
        "email": "newstaff@test.com",
        "password": "StaffPass123",
        "full_name": "New Branch Staff",
        "phone": "9988776655",
        "branch_id": b1_id,
    }
    response = client.post("/auth/staff", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "BRANCH_STAFF"
    assert data["branch_id"] == b1_id


def test_create_staff_authorization_failure(client, seed_test_data, customer_headers):
    # Mandatory requirement: one authorisation (wrong role) test
    payload = {
        "email": "hacker@test.com",
        "password": "StaffPass123",
        "full_name": "Fake Staff",
        "phone": "9988776655",
        "branch_id": seed_test_data["b1"].id,
    }
    response = client.post("/auth/staff", json=payload, headers=customer_headers)
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_verify_customer_licence_by_branch_staff(client, seed_test_data, staff1_headers):
    # User story 4: As a branch staff member, verify a customer's licence
    unverified_id = seed_test_data["cust_unverified"].id
    response = client.patch(f"/customers/{unverified_id}/verify-licence", headers=staff1_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == unverified_id
    assert data["licence_verified"] is True
