import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from petgarden.config import Settings
from petgarden.main import create_app


@pytest.fixture()
def settings() -> Settings:
    return Settings(data_dir=Path(tempfile.mkdtemp(prefix="petgarden-test-")))


@pytest.fixture()
def app(settings: Settings):
    return create_app(settings)


@pytest.fixture()
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def class_id(client: TestClient) -> int:
    resp = client.post("/api/classes", json={"name": "四年级一班", "color": "moss"})
    assert resp.status_code == 201, resp.text
    return resp.json()["class"]["id"]


@pytest.fixture()
def student_id(client: TestClient, class_id: int) -> int:
    resp = client.post(
        f"/api/classes/{class_id}/students",
        json={"name": "林小满", "student_no": "03", "seat_no": 3, "species": "cat"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["student"]["id"]