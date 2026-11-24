from unittest.mock import Mock
from sqlalchemy.exc import OperationalError
from app.db.session import get_db
from app.main import app

def test_health_reports_service_and_database_up(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["database"] == "connected" and r.json()["service"] == "vehicle-rental-management-system"

def test_health_reports_database_down(client):
    db = Mock()
    db.execute.side_effect = OperationalError("SELECT 1", {}, Exception())
    def _db(): yield db
    app.dependency_overrides[get_db] = _db
    try:
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "degraded" and r.json()["database"].startswith("unhealthy:")
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_openapi_docs_are_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200 and r.json()["info"]["title"] == "Vehicle Rental Management System" and "/health" in r.json()["paths"]
