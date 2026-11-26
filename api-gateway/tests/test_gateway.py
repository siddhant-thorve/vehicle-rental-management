from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from gateway.service_addresses import SERVICES
from main import app


def test_req_G01_catalog_paths_route_to_catalog_service():
    assert SERVICES["vehicle-categories"] == "http://127.0.0.1:8005"
    assert SERVICES["tariffs"] == "http://127.0.0.1:8005"


def test_unknown_service_prefix_returns_not_found():
    client = TestClient(app)

    response = client.get("/not-a-service")

    assert response.status_code == 404


def test_vehicle_route_forwards_to_fleet_service(monkeypatch):
    received = {}

    async def fake_forward_request(service_url, request, service_path):
        received["service_url"] = service_url
        received["method"] = request.method
        received["service_path"] = service_path
        return JSONResponse({"forwarded": True})

    monkeypatch.setattr("gateway.fleet_routes.forward_request", fake_forward_request)

    response = TestClient(app).get("/vehicles/7")

    assert response.status_code == 200
    assert response.json() == {"forwarded": True}
    assert received == {
        "service_url": "http://127.0.0.1:8002",
        "method": "GET",
        "service_path": "vehicles/7",
    }


def test_my_bookings_route_is_forwarded_to_booking_service(monkeypatch):
    received = {}

    async def fake_forward_request(service_url, request, service_path):
        received["service_url"] = service_url
        received["service_path"] = service_path
        return JSONResponse([])

    monkeypatch.setattr("gateway.booking_routes.forward_request", fake_forward_request)

    response = TestClient(app).get("/bookings/me")

    assert response.status_code == 200
    assert response.json() == []
    assert received == {
        "service_url": "http://127.0.0.1:8003",
        "service_path": "bookings/me",
    }


def test_openapi_json_includes_health_and_remote_service_paths(monkeypatch):
    class OfflineServices:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            class Response:
                status_code = 200

                @staticmethod
                def json():
                    return {
                        "paths": {
                            "/vehicles": {
                                "get": {
                                    "summary": "List vehicles",
                                    "responses": {"200": {"description": "OK"}},
                                }
                            }
                        },
                        "components": {"schemas": {}},
                    }

            return Response()

    monkeypatch.setattr(
        "gateway.openapi_docs.httpx.Client",
        lambda **kwargs: OfflineServices(),
    )
    app.openapi_schema = None

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/health" in response.json()["paths"]
    assert "/vehicles" in response.json()["paths"]
    app.openapi_schema = None
