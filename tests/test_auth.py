def test_customer_registration_success(client, seed_test_data):
    p = {"email": "newuser@test.com", "password": "Password@123", "full_name": "New Cust", "phone": "9998887770", "licence_no": "KA012022001122"}
    r = client.post("/auth/register", json=p)
    assert r.status_code == 201 and r.json()["email"] == p["email"] and r.json()["role"] == "CUSTOMER" and r.json()["licence_verified"] is False

def test_customer_registration_duplicate_email(client, seed_test_data):
    p = {"email": "verified@test.com", "password": "Password@123", "full_name": "Dup User", "phone": "9998887771", "licence_no": "KA012022001123"}
    r = client.post("/auth/register", json=p)
    assert r.status_code == 409 and r.json()["code"] == "CONFLICT"

def test_login_success(client, seed_test_data):
    r = client.post("/auth/login", json={"email": "admin@test.com", "password": "AdminPass123"})
    assert r.status_code == 200 and "access_token" in r.json() and r.json()["role"] == "ADMIN" and r.json()["token_type"] == "bearer"

def test_authentication_failure_wrong_password(client, seed_test_data):
    r = client.post("/auth/login", json={"email": "admin@test.com", "password": "WrongPassword!"})
    assert r.status_code == 401 and r.json()["code"] == "UNAUTHORIZED"

def test_create_staff_by_admin(client, seed_test_data, admin_headers):
    bid = seed_test_data["b1"].id
    p = {"email": "newstaff@test.com", "password": "StaffPass123", "full_name": "New Staff", "phone": "9988776655", "branch_id": bid}
    r = client.post("/auth/staff", json=p, headers=admin_headers)
    assert r.status_code == 201 and r.json()["role"] == "BRANCH_STAFF" and r.json()["branch_id"] == bid

def test_create_staff_authorization_failure(client, seed_test_data, customer_headers):
    p = {"email": "hacker@test.com", "password": "StaffPass123", "full_name": "Fake", "phone": "9988776655", "branch_id": seed_test_data["b1"].id}
    r = client.post("/auth/staff", json=p, headers=customer_headers)
    assert r.status_code == 403 and r.json()["code"] == "FORBIDDEN"

def test_verify_customer_licence_by_branch_staff(client, seed_test_data, staff1_headers):
    uid = seed_test_data["cust_unverified"].id
    r = client.patch(f"/customers/{uid}/verify-licence", headers=staff1_headers)
    assert r.status_code == 200 and r.json()["id"] == uid and r.json()["licence_verified"] is True
