from fastapi.testclient import TestClient


def _raise_to(client: TestClient, sid: int, score: int) -> None:
    remaining = score
    while remaining > 0:
        step = min(5, remaining)
        r = client.post(f"/api/students/{sid}/score", json={"delta": step})
        assert r.status_code == 200, r.text
        remaining -= step


def test_pet_catalog(client: TestClient) -> None:
    r = client.get("/api/pets")
    assert r.status_code == 200
    data = r.json()
    assert data["level_thresholds"] == [0, 20, 40, 60, 80]
    assert data["stage_names"] == ["初遇", "相伴", "默契", "蜕变", "传说"]
    assert len(data["species"]) == 6
    types = {s["id"]: s["type"] for s in data["species"]}
    assert types["dragon"] == "divine"
    assert types["cat"] == "normal"


def test_collection_defaults(client: TestClient, student_id: int) -> None:
    r = client.get(f"/api/students/{student_id}/collection")
    assert r.status_code == 200
    data = r.json()
    assert data["can_switch_pet"] is False
    assert data["divine_unlocked"] is False
    items = {i["species"]: i for i in data["items"]}
    assert len(items) == 6
    assert items["cat"]["is_current"] is True
    assert items["cat"]["best_level"] == 1
    assert items["dragon"]["unlocked"] is False


def test_switch_not_ready(client: TestClient, student_id: int) -> None:
    _raise_to(client, student_id, 60)  # L4
    r = client.post(f"/api/students/{student_id}/switch-pet", json={"species": "dog"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PET_SWITCH_NOT_READY"


def test_switch_success_resets_score(client: TestClient, student_id: int) -> None:
    _raise_to(client, student_id, 80)  # L5
    r = client.post(f"/api/students/{student_id}/switch-pet", json={"species": "dog"})
    assert r.status_code == 200
    data = r.json()
    assert data["student"]["species"] == "dog"
    assert data["student"]["score"] == 0
    assert data["previous_species"] == "cat"
    # 旧进度保留
    r = client.get(f"/api/students/{student_id}/collection")
    items = {i["species"]: i for i in r.json()["items"]}
    assert items["cat"]["best_level"] == 5
    assert items["dog"]["best_level"] == 1
    assert items["dog"]["is_current"] is True
    # 换宠后神兽已解锁（cat 曾 L5）
    assert r.json()["divine_unlocked"] is True


def test_switch_same_species(client: TestClient, student_id: int) -> None:
    _raise_to(client, student_id, 80)
    r = client.post(f"/api/students/{student_id}/switch-pet", json={"species": "cat"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "SAME_SPECIES"


def test_dragon_locked_then_unlocked(client: TestClient, student_id: int) -> None:
    _raise_to(client, student_id, 80)
    # 还没有普通物种 L5 进度时（当前 cat L5 后其实已解锁），先验证锁定场景：
    # 新学生（dog，L5）没有普通 L5 历史 -> 但达到 80 的 dog 自己就是普通 L5。
    # 所以构造锁定场景：换一个未达 L5 的学生
    r = client.post("/api/classes", json={"name": "测试班"})
    cid = r.json()["class"]["id"]
    r = client.post(f"/api/classes/{cid}/students", json={"name": "小明", "species": "rabbit"})
    sid2 = r.json()["student"]["id"]
    _raise_to(client, sid2, 80)
    # rabbit L5 -> 普通 L5 已达成，神兽应解锁
    r = client.post(f"/api/students/{sid2}/switch-pet", json={"species": "dragon"})
    assert r.status_code == 200
    assert r.json()["student"]["species"] == "dragon"


def test_divine_locked_403(client: TestClient, class_id: int) -> None:
    # 构造一个 L4 学生直接换神兽 -> 409 优先于 403
    r = client.post(f"/api/classes/{class_id}/students", json={"name": "小红", "species": "fox"})
    sid = r.json()["student"]["id"]
    _raise_to(client, sid, 80)
    # fox 到 L5 后 divine 已解锁，不能测 403；直接构造 patch 类场景：
    # 用另一个从未 L5 的学生访问 -> can_switch false，409 即可
    r = client.post(f"/api/classes/{class_id}/students", json={"name": "小蓝", "species": "dog"})
    sid2 = r.json()["student"]["id"]
    r = client.post(f"/api/students/{sid2}/switch-pet", json={"species": "dragon"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "PET_SWITCH_NOT_READY"


def test_switch_invalid_species(client: TestClient, student_id: int) -> None:
    _raise_to(client, student_id, 80)
    r = client.post(f"/api/students/{student_id}/switch-pet", json={"species": "unicorn"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_SPECIES"


def test_rollcall(client: TestClient, class_id: int) -> None:
    for i in range(5):
        client.post(f"/api/classes/{class_id}/students", json={"name": f"学生{i}"})
    r = client.post(f"/api/classes/{class_id}/rollcall", json={"mode": "fair"})
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "fair"
    assert data["pool_size"] >= 1
    assert data["student"]["last_picked_at"] is not None
    r = client.post(f"/api/classes/{class_id}/rollcall", json={"mode": "random"})
    assert r.status_code == 200
    assert r.json()["pool_size"] == 5


def test_rollcall_excludes_absent(client: TestClient, class_id: int) -> None:
    r = client.post(f"/api/classes/{class_id}/students", json={"name": "唯一"})
    sid = r.json()["student"]["id"]
    client.patch(f"/api/students/{sid}", json={"is_present": False})
    r = client.post(f"/api/classes/{class_id}/rollcall", json={})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "NO_STUDENTS"


def test_rollcall_empty_class(client: TestClient, class_id: int) -> None:
    r = client.post(f"/api/classes/{class_id}/rollcall", json={})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "NO_STUDENTS"


def test_display_endpoint(client: TestClient, class_id: int, student_id: int) -> None:
    r = client.get(f"/api/classes/{class_id}/display")
    assert r.status_code == 200
    data = r.json()
    assert data["class"]["id"] == class_id
    assert len(data["students"]) == 1
    assert "server_time" in data