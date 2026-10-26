import json

from fastapi.testclient import TestClient


def _export(client: TestClient) -> dict:
    r = client.get("/api/export")
    assert r.status_code == 200
    return r.json()


def test_export_format(client: TestClient, class_id: int, student_id: int) -> None:
    client.post(f"/api/students/{student_id}/score", json={"delta": 1})
    data = _export(client)
    assert data["format"] == "petgarden-backup"
    assert data["version"] == 1
    raw = json.dumps(data, ensure_ascii=False)
    assert "pin" not in raw
    assert "secret" not in raw
    assert len(data["classes"]) == 1
    assert len(data["students"]) == 1
    assert len(data["score_events"]) == 1
    assert len(data["pet_progress"]) == 1
    assert "teacher_name" not in data["settings"]


def test_import_requires_confirm(client: TestClient) -> None:
    data = _export(client)
    r = client.post("/api/import", json={"confirm": "NO", "backup": data})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "IMPORT_CONFIRM_REQUIRED"


def test_import_roundtrip(client: TestClient, class_id: int, student_id: int) -> None:
    client.post(f"/api/students/{student_id}/score", json={"delta": 5})
    data = _export(client)

    # 破坏现有数据
    client.request("DELETE", f"/api/classes/{class_id}", json={"confirm_name": "四年级一班"})
    assert client.get("/api/classes").json()["classes"] == []

    r = client.post("/api/import", json={"confirm": "REPLACE", "backup": data})
    assert r.status_code == 200
    assert r.json()["counts"]["students"] == 1
    classes = client.get("/api/classes").json()["classes"]
    assert len(classes) == 1
    assert classes[0]["name"] == "四年级一班"
    stu = client.get(f"/api/classes/{class_id}/students").json()["students"][0]
    assert stu["score"] == 5


def test_import_invalid_rolls_back(client: TestClient, class_id: int) -> None:
    bad = {
        "format": "petgarden-backup",
        "version": 1,
        "classes": [],
        "students": [{"id": 1, "class_id": 99}],
        "pet_progress": [],
        "score_events": [],
    }
    r = client.post("/api/import", json={"confirm": "REPLACE", "backup": bad})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "IMPORT_INVALID"
    # 原数据不变
    assert len(client.get("/api/classes").json()["classes"]) == 1

    r = client.post("/api/import", json={"confirm": "REPLACE", "backup": {"format": "x"}})
    assert r.status_code == 422


def test_import_writes_pre_backup(client: TestClient, class_id: int) -> None:
    data = _export(client)
    r = client.post("/api/import", json={"confirm": "REPLACE", "backup": data})
    assert r.status_code == 200
    backups_dir = client.get("/api/settings").json()["data_dir"]
    import pathlib

    backups = list((pathlib.Path(backups_dir) / "backups").glob("pre-import-*.json"))
    assert len(backups) >= 1


def test_settings_patch(client: TestClient) -> None:
    r = client.patch("/api/settings", json={"motion_pref": "reduced"})
    assert r.status_code == 200
    data = r.json()
    assert data["motion_pref"] == "reduced"
    r = client.get("/api/settings")
    assert r.json()["motion_pref"] == "reduced"