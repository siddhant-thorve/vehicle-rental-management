from fastapi.testclient import TestClient

from main import SERVICES, app


def test_req_G01_catalog_paths_route_to_catalog_service():
    assert SERVICES["vehicle-categories"] == "http://127.0.0.1:8005"
    assert SERVICES["tariffs"] == "http://127.0.0.1:8005"


def test_unknown_service_prefix_returns_not_found():
    client = TestClient(app)

    response = client.get("/not-a-service")

    assert response.status_code == 404
