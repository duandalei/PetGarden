from fastapi.testclient import TestClient


def _score(client: TestClient, sid: int, delta: int, reason: str | None = None):
    return client.post(f"/api/students/{sid}/score", json={"delta": delta, "reason": reason})


def test_score_plus_minus(client: TestClient, student_id: int) -> None:
    r = _score(client, student_id, 1, "课堂积极")
    assert r.status_code == 200
    data = r.json()
    assert data["student"]["score"] == 1
    assert data["event"]["delta"] == 1
    assert data["event"]["score_before"] == 0
    assert data["event"]["score_after"] == 1
    assert data["event"]["reason"] == "课堂积极"
    assert data["level_up"] is False
    assert data["can_undo"] is True

    r = _score(client, student_id, -1)
    assert r.status_code == 200
    assert r.json()["student"]["score"] == 0


def test_score_at_limit(client: TestClient, student_id: int) -> None:
    # 0 分再减
    r = _score(client, student_id, -1)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "SCORE_AT_LIMIT"
    # 加到 100（每次 +5，恰好 20 次到 100）
    for _ in range(20):
        r = _score(client, student_id, 5)
        assert r.status_code == 200
    # 再加 → 409
    r = _score(client, student_id, 5)
    assert r.status_code == 409
    r = client.get(f"/api/students/{student_id}")
    assert r.json()["student"]["score"] == 100
    # 事件数 = 20（最后一次 409 不写事件）
    events = r.json()["recent_events"]
    assert all(e["undone_at"] is None for e in events)


def test_level_stage_mood_transition(client: TestClient, student_id: int) -> None:
    # 19 -> 20 触发升级
    for _ in range(19):
        _score(client, student_id, 1)
    r = _score(client, student_id, 1)
    data = r.json()
    assert data["student"]["score"] == 20
    assert data["student"]["level"] == 2
    assert data["student"]["stage"] == "相伴"
    assert data["level_up"] is True
    assert data["stage_changed"] is True
    # 60 分心情变 happy
    for _ in range(40):
        _score(client, student_id, 1)
    r = client.get(f"/api/students/{student_id}")
    assert r.json()["student"]["mood"] == "happy"


def test_best_level_sync_and_undo_keeps_best(client: TestClient, student_id: int) -> None:
    for _ in range(20):
        _score(client, student_id, 1)
    r = client.get(f"/api/students/{student_id}")
    assert r.json()["student"]["best_level"] == 2
    # 撤销到 0，best_level 不降
    r = client.get(f"/api/students/{student_id}")
    events = r.json()["recent_events"]
    for e in events:
        if e["undone_at"] is None:
            client.post(f"/api/score-events/{e['id']}/undo")
            break
    r = client.get(f"/api/students/{student_id}")
    stu = r.json()["student"]
    assert stu["score"] == 19
    assert stu["level"] == 1
    assert stu["best_level"] == 2  # 图鉴记录不下降


def test_undo_success(client: TestClient, student_id: int) -> None:
    r = _score(client, student_id, 1)
    eid = r.json()["event"]["id"]
    r = client.post(f"/api/score-events/{eid}/undo")
    assert r.status_code == 200
    assert r.json()["student"]["score"] == 0
    assert r.json()["event"]["undone_at"] is not None


def test_undo_twice(client: TestClient, student_id: int) -> None:
    r = _score(client, student_id, 1)
    eid = r.json()["event"]["id"]
    client.post(f"/api/score-events/{eid}/undo")
    r = client.post(f"/api/score-events/{eid}/undo")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EVENT_ALREADY_UNDONE"


def test_undo_not_latest(client: TestClient, student_id: int) -> None:
    r1 = _score(client, student_id, 1)
    eid1 = r1.json()["event"]["id"]
    _score(client, student_id, 1)
    r = client.post(f"/api/score-events/{eid1}/undo")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EVENT_NOT_LATEST"


def test_undo_event_not_found(client: TestClient) -> None:
    r = client.post("/api/score-events/999/undo")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "EVENT_NOT_FOUND"


def test_invalid_delta(client: TestClient, student_id: int) -> None:
    r = _score(client, student_id, 0)
    assert r.status_code == 422
    r = _score(client, student_id, 6)
    assert r.status_code == 422