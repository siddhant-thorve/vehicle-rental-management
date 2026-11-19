from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client() -> Generator[tuple[TestClient, Mock], None, None]:
    db = Mock()

    def override_get_db() -> Generator[Mock, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client, db
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_health_reports_service_and_database_up(
    client: tuple[TestClient, Mock],
) -> None:
    test_client, _ = client
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "UP", "database": "UP"}


def test_health_reports_database_down(client: tuple[TestClient, Mock]) -> None:
    test_client, db = client
    db.execute.side_effect = OperationalError("SELECT 1", {}, Exception())

    response = test_client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"service": "UP", "database": "DOWN"}


def test_openapi_docs_are_available(client: tuple[TestClient, Mock]) -> None:
    test_client, _ = client
    response = test_client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Vehicle Rental Management System API"
    assert "/health" in response.json()["paths"]
