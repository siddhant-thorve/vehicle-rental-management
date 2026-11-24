from datetime import date, timedelta

def test_health_check_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["database"] == "connected"

def test_utilisation_report_by_admin(client, seed_test_data, admin_headers):
    today = date.today().isoformat()
    r = client.get(f"/reports/utilisation?from={(date.today() - timedelta(days=7)).isoformat()}&to={today}", headers=admin_headers)
    assert r.status_code == 200 and len(r.json()["branches"]) >= 2 and any(b["branch_name"] == "Mumbai Branch" for b in r.json()["branches"])

def test_revenue_report_by_admin(client, seed_test_data, admin_headers):
    today = date.today().isoformat()
    r = client.get(f"/reports/revenue?from={(date.today() - timedelta(days=30)).isoformat()}&to={today}", headers=admin_headers)
    assert r.status_code == 200 and "total_revenue" in r.json() and "breakdown" in r.json()

def test_reports_forbidden_for_staff_and_customer(client, seed_test_data, customer_headers, staff1_headers):
    t = date.today().isoformat()
    assert client.get(f"/reports/utilisation?from={t}&to={t}", headers=customer_headers).status_code == 403
    assert client.get(f"/reports/revenue?from={t}&to={t}", headers=staff1_headers).status_code == 403
