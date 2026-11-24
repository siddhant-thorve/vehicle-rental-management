def test_create_branch_success(client, seed_test_data, admin_headers):
    p = {"name": "Pune Branch", "city": "Pune", "address": "Shivaji Nagar", "contact_no": "9876543299"}
    r = client.post("/branches", json=p, headers=admin_headers)
    assert r.status_code == 201 and r.json()["name"] == "Pune Branch" and r.json()["city"] == "Pune"

def test_validation_failure_short_name(client, seed_test_data, admin_headers):
    p = {"name": "P", "city": "Pune", "address": "Shivaji Nagar", "contact_no": "9876543299"}
    r = client.post("/branches", json=p, headers=admin_headers)
    assert r.status_code == 422 and r.json()["code"] == "VALIDATION_ERROR"

def test_list_branches_with_pagination_and_filter(client, seed_test_data):
    r = client.get("/branches?city=Mumbai&page=1&size=10")
    assert r.status_code == 200 and r.json()["total"] >= 1 and any(b["city"] == "Mumbai" for b in r.json()["items"])

def test_update_branch_by_admin(client, seed_test_data, admin_headers):
    r = client.patch(f"/branches/{seed_test_data['b1'].id}", json={"address": "Updated 123"}, headers=admin_headers)
    assert r.status_code == 200 and r.json()["address"] == "Updated 123"

def test_create_branch_forbidden_for_customer(client, seed_test_data, customer_headers):
    p = {"name": "Unauthorized", "city": "Goa", "address": "Panaji", "contact_no": "9876543288"}
    assert client.post("/branches", json=p, headers=customer_headers).status_code == 403
