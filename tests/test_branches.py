def test_create_branch_success(client, seed_test_data, admin_headers):
    # User story 5: As an admin, create and update branches
    payload = {
        "name": "Pune Branch",
        "city": "Pune",
        "address": "Shivaji Nagar, Pune 411005",
        "contact_no": "9876543299",
    }
    response = client.post("/branches", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Pune Branch"
    assert data["city"] == "Pune"


def test_validation_failure_short_name(client, seed_test_data, admin_headers):
    # Mandatory requirement: one validation failure test
    payload = {
        "name": "P",  # violates min_length=2
        "city": "Pune",
        "address": "Shivaji Nagar",
        "contact_no": "9876543299",
    }
    response = client.post("/branches", json=payload, headers=admin_headers)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_list_branches_with_pagination_and_filter(client, seed_test_data):
    response = client.get("/branches?city=Mumbai&page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert any(b["city"] == "Mumbai" for b in data["items"])


def test_update_branch_by_admin(client, seed_test_data, admin_headers):
    b1_id = seed_test_data["b1"].id
    payload = {"address": "Updated Address 123"}
    response = client.patch(f"/branches/{b1_id}", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["address"] == "Updated Address 123"


def test_create_branch_forbidden_for_customer(client, seed_test_data, customer_headers):
    payload = {
        "name": "Unauthorized Branch",
        "city": "Goa",
        "address": "Panaji, Goa",
        "contact_no": "9876543288",
    }
    response = client.post("/branches", json=payload, headers=customer_headers)
    assert response.status_code == 403
