from datetime import date, timedelta


def test_health_check_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_utilisation_report_by_admin(client, seed_test_data, admin_headers):
    # User story 22: As an admin, fleet utilisation report per branch for a date range
    today = date.today()
    from_date = (today - timedelta(days=7)).isoformat()
    to_date = today.isoformat()

    resp = client.get(f"/reports/utilisation?from={from_date}&to={to_date}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "branches" in data
    assert len(data["branches"]) >= 2
    assert any(b["branch_name"] == "Mumbai Branch" for b in data["branches"])


def test_revenue_report_by_admin(client, seed_test_data, admin_headers):
    # User story 23: As an admin, revenue report grouped by branch and category
    today = date.today()
    from_date = (today - timedelta(days=30)).isoformat()
    to_date = today.isoformat()

    resp = client.get(f"/reports/revenue?from={from_date}&to={to_date}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_revenue" in data
    assert "breakdown" in data


def test_reports_forbidden_for_staff_and_customer(client, seed_test_data, customer_headers, staff1_headers):
    today = date.today().isoformat()
    resp1 = client.get(f"/reports/utilisation?from={today}&to={today}", headers=customer_headers)
    assert resp1.status_code == 403

    resp2 = client.get(f"/reports/revenue?from={today}&to={today}", headers=staff1_headers)
    assert resp2.status_code == 403
