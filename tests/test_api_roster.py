from fastapi.testclient import TestClient


def test_class_crud(client: TestClient) -> None:
    r = client.post("/api/classes", json={"name": "四年级一班", "color": "clay"})
    assert r.status_code == 201
    cls = r.json()["class"]
    assert cls["name"] == "四年级一班"
    assert cls["student_count"] == 0

    r = client.get("/api/classes")
    assert len(r.json()["classes"]) == 1

    r = client.patch(f"/api/classes/{cls['id']}", json={"name": "四年级二班", "grade": "四年级"})
    assert r.status_code == 200
    assert r.json()["class"]["name"] == "四年级二班"
    assert r.json()["class"]["grade"] == "四年级"

    # 删除需输入名称确认
    r = client.request("DELETE", f"/api/classes/{cls['id']}", json={"confirm_name": "错误名称"})
    assert r.status_code == 409
    r = client.request("DELETE", f"/api/classes/{cls['id']}", json={"confirm_name": "四年级二班"})
    assert r.status_code == 204
    r = client.get("/api/classes")
    assert r.json()["classes"] == []


def test_class_not_found(client: TestClient) -> None:
    r = client.get("/api/classes/999")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CLASS_NOT_FOUND"


def test_student_crud(client: TestClient, class_id: int) -> None:
    r = client.post(
        f"/api/classes/{class_id}/students",
        json={"name": "林小满", "student_no": "03", "seat_no": 3},
    )
    assert r.status_code == 201
    stu = r.json()["student"]
    assert stu["score"] == 0
    assert stu["level"] == 1
    assert stu["stage"] == "初遇"
    assert stu["mood"] == "sad"
    assert stu["species"] in ("cat", "dog", "rabbit", "panda", "fox")
    assert stu["best_level"] == 1
    assert stu["can_switch_pet"] is False

    # 重复学号
    r = client.post(
        f"/api/classes/{class_id}/students", json={"name": "张三", "student_no": "03"}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DUPLICATE_STUDENT_NO"

    # 编辑
    r = client.patch(
        f"/api/students/{stu['id']}", json={"name": "林小满2", "seat_no": 5}
    )
    assert r.status_code == 200
    assert r.json()["student"]["name"] == "林小满2"
    assert r.json()["student"]["seat_no"] == 5

    # 详情含最近事件
    r = client.get(f"/api/students/{stu['id']}")
    assert r.status_code == 200
    assert "recent_events" in r.json()

    # 删除
    r = client.delete(f"/api/students/{stu['id']}")
    assert r.status_code == 204
    r = client.get(f"/api/students/{stu['id']}")
    assert r.status_code == 404


def test_student_sort_search(client: TestClient, class_id: int) -> None:
    for name, no, seat in [("张三", "01", 2), ("李四", "02", 1), ("王五", None, None)]:
        client.post(
            f"/api/classes/{class_id}/students",
            json={"name": name, "student_no": no, "seat_no": seat},
        )
    r = client.get(f"/api/classes/{class_id}/students?sort=seat")
    seats = [s["seat_no"] for s in r.json()["students"]]
    assert seats == [1, 2, None]
    r = client.get(f"/api/classes/{class_id}/students?sort=name")
    names = [s["name"] for s in r.json()["students"]]
    assert names == sorted(names)
    r = client.get(f"/api/classes/{class_id}/students?q=张")
    assert len(r.json()["students"]) == 1
    r = client.get(f"/api/classes/{class_id}/students?q=02")
    assert len(r.json()["students"]) == 1


def test_bulk_import_preview_and_commit(client: TestClient, class_id: int) -> None:
    client.post(
        f"/api/classes/{class_id}/students", json={"name": "已存在", "student_no": "01"}
    )
    text = "林小满,03\n陈一诺，04\n王梓涵\t05\t5\n,06\n\n已存在,01\n好座位,07,150"
    r = client.post(
        f"/api/classes/{class_id}/students/bulk", json={"text": text, "preview": True}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["preview"] is True
    assert len(data["created"]) == 3
    reasons = {item["reason"] for item in data["skipped"]}
    assert "DUPLICATE_STUDENT_NO" in reasons
    assert "EMPTY_LINE" in reasons
    error_reasons = {item["reason"] for item in data["errors"]}
    assert "EMPTY_NAME" in error_reasons
    assert "INVALID_SEAT" in error_reasons
    # 预览不落库
    r = client.get(f"/api/classes/{class_id}/students")
    assert len(r.json()["students"]) == 1

    r = client.post(
        f"/api/classes/{class_id}/students/bulk", json={"text": text, "preview": False}
    )
    data = r.json()
    assert data["preview"] is False
    assert len(data["created"]) == 3
    r = client.get(f"/api/classes/{class_id}/students")
    assert len(r.json()["students"]) == 4


def test_delete_class_cascades(client: TestClient, class_id: int) -> None:
    r = client.post(f"/api/classes/{class_id}/students", json={"name": "林小满"})
    sid = r.json()["student"]["id"]
    client.post(f"/api/students/{sid}/score", json={"delta": 1})
    r = client.request("DELETE", f"/api/classes/{class_id}", json={"confirm_name": "四年级一班"})
    assert r.status_code == 204
    r = client.get(f"/api/students/{sid}")
    assert r.status_code == 404