def test_req_F01_customer_registration(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "new-customer@example.com",
            "password": "valid-password",
            "full_name": "New Customer",
            "phone": "1234567890",
            "licence_no": "AB123456789",
        },
    )

    assert response.status_code == 201
    assert response.json()["licence_no"] == "AB****6789"


def test_req_F02_login_returns_access_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "new-customer@example.com",
            "password": "valid-password",
            "full_name": "New Customer",
            "phone": "1234567890",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "new-customer@example.com", "password": "valid-password"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_req_F03_admin_creates_staff_linked_to_branch(client):
    response = client.post(
        "/auth/staff",
        json={
            "email": "branch-staff@example.com",
            "password": "valid-password",
            "full_name": "Branch Staff",
            "phone": "1234567890",
            "branch_id": 7,
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "BRANCH_STAFF"
    assert response.json()["branch_id"] == 7


def test_req_F04_branch_staff_verifies_customer_licence(client, user_data):
    customer = client.post(
        "/auth/register",
        json={
            "email": "customer@example.com",
            "password": "valid-password",
            "full_name": "Test Customer",
            "phone": "1234567890",
            "licence_no": "AB123456789",
        },
    ).json()
    user_data["role"] = "BRANCH_STAFF"

    response = client.patch(
        f"/customers/{customer['id']}/verify-licence",
    )

    assert response.status_code == 200
    assert response.json()["licence_verified"] is True
    assert response.json()["licence_no"] == "AB****6789"
