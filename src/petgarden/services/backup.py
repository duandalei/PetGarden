"""数据导出/导入服务。"""

import json
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from petgarden.db import get_setting, set_setting, utcnow
from petgarden.errors import AppError
from petgarden.models import Class, PetProgress, ScoreEvent, Student

EXPORT_FORMAT = "petgarden-backup"
EXPORT_VERSION = 1
MAX_IMPORT_BYTES = 5 * 1024 * 1024

_SETTINGS_KEYS = ("motion_pref", "display_sort")


def build_export(db: Session) -> dict:
    classes = db.scalars(select(Class).order_by(Class.id)).all()
    students = db.scalars(select(Student).order_by(Student.id)).all()
    progress = db.scalars(select(PetProgress)).all()
    events = db.scalars(select(ScoreEvent).order_by(ScoreEvent.id)).all()
    return {
        "format": EXPORT_FORMAT,
        "version": EXPORT_VERSION,
        "exported_at": utcnow(),
        "settings": {key: get_setting(db, key, "") for key in _SETTINGS_KEYS},
        "classes": [
            {
                "id": c.id,
                "name": c.name,
                "grade": c.grade,
                "color": c.color,
                "sort_order": c.sort_order,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in classes
        ],
        "students": [
            {
                "id": s.id,
                "class_id": s.class_id,
                "name": s.name,
                "student_no": s.student_no,
                "seat_no": s.seat_no,
                "score": s.score,
                "species": s.species,
                "is_present": s.is_present,
                "last_picked_at": s.last_picked_at,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            for s in students
        ],
        "pet_progress": [
            {
                "student_id": p.student_id,
                "species": p.species,
                "best_level": p.best_level,
                "first_reached_at": p.first_reached_at,
                "last_reached_at": p.last_reached_at,
            }
            for p in progress
        ],
        "score_events": [
            {
                "id": e.id,
                "class_id": e.class_id,
                "student_id": e.student_id,
                "delta": e.delta,
                "score_before": e.score_before,
                "score_after": e.score_after,
                "reason": e.reason,
                "created_at": e.created_at,
                "undone_at": e.undone_at,
            }
            for e in events
        ],
    }


def validate_backup(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise AppError(422, "IMPORT_INVALID", "备份文件格式不正确。")
    if payload.get("format") != EXPORT_FORMAT:
        raise AppError(422, "IMPORT_INVALID", "不是 PetGarden 的备份文件。")
    if payload.get("version") != EXPORT_VERSION:
        raise AppError(422, "IMPORT_INVALID", "备份版本不兼容。")
    for key in ("classes", "students", "pet_progress", "score_events"):
        if not isinstance(payload.get(key), list):
            raise AppError(422, "IMPORT_INVALID", f"备份缺少 {key} 数据。")
    class_ids = set()
    for c in payload["classes"]:
        if not isinstance(c, dict) or not isinstance(c.get("id"), int) or not c.get("name"):
            raise AppError(422, "IMPORT_INVALID", "班级数据不完整。")
        class_ids.add(c["id"])
    student_ids = set()
    for s in payload["students"]:
        if (
            not isinstance(s, dict)
            or not isinstance(s.get("id"), int)
            or s.get("class_id") not in class_ids
            or not s.get("name")
        ):
            raise AppError(422, "IMPORT_INVALID", "学生数据不完整或班级缺失。")
        if not isinstance(s.get("score"), int) or not 0 <= s["score"] <= 100:
            raise AppError(422, "IMPORT_INVALID", "学生积分超出范围。")
        student_ids.add(s["id"])
    for p in payload["pet_progress"]:
        if not isinstance(p, dict) or p.get("student_id") not in student_ids:
            raise AppError(422, "IMPORT_INVALID", "宠物进度数据引用了不存在的学生。")
        if not isinstance(p.get("best_level"), int) or not 1 <= p["best_level"] <= 5:
            raise AppError(422, "IMPORT_INVALID", "宠物进度等级超出范围。")
    for e in payload["score_events"]:
        if (
            not isinstance(e, dict)
            or not isinstance(e.get("id"), int)
            or e.get("student_id") not in student_ids
            or e.get("class_id") not in class_ids
        ):
            raise AppError(422, "IMPORT_INVALID", "积分事件数据不完整。")
    return payload


def write_pre_import_backup(db: Session, backups_dir: Path) -> Path:
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = utcnow().replace(":", "").replace("-", "").replace("T", "-").rstrip("Z")
    path = backups_dir / f"pre-import-{stamp}.json"
    path.write_text(
        json.dumps(build_export(db), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def import_backup(db: Session, payload: dict) -> dict:
    """在单事务内替换全部数据；调用方负责提交/回滚。"""
    now = utcnow()
    db.execute(delete(ScoreEvent))
    db.execute(delete(PetProgress))
    db.execute(delete(Student))
    db.execute(delete(Class))
    for c in payload["classes"]:
        db.add(
            Class(
                id=c["id"],
                name=c["name"],
                grade=c.get("grade"),
                color=c.get("color") or "moss",
                sort_order=c.get("sort_order") or 0,
                created_at=c.get("created_at") or now,
                updated_at=c.get("updated_at") or now,
            )
        )
    db.flush()
    for s in payload["students"]:
        db.add(
            Student(
                id=s["id"],
                class_id=s["class_id"],
                name=s["name"],
                student_no=s.get("student_no"),
                seat_no=s.get("seat_no"),
                score=s["score"],
                species=s["species"],
                is_present=1 if s.get("is_present", 1) else 0,
                last_picked_at=s.get("last_picked_at"),
                created_at=s.get("created_at") or now,
                updated_at=s.get("updated_at") or now,
            )
        )
    db.flush()
    for p in payload["pet_progress"]:
        db.add(
            PetProgress(
                student_id=p["student_id"],
                species=p["species"],
                best_level=p["best_level"],
                first_reached_at=p.get("first_reached_at") or now,
                last_reached_at=p.get("last_reached_at") or now,
            )
        )
    db.flush()
    for e in payload["score_events"]:
        db.add(
            ScoreEvent(
                id=e["id"],
                class_id=e["class_id"],
                student_id=e["student_id"],
                delta=e["delta"],
                score_before=e["score_before"],
                score_after=e["score_after"],
                reason=e.get("reason"),
                created_at=e.get("created_at") or now,
                undone_at=e.get("undone_at"),
            )
        )
    settings = payload.get("settings")
    if isinstance(settings, dict):
        for key in _SETTINGS_KEYS:
            value = settings.get(key)
            if isinstance(value, str) and value:
                set_setting(db, key, value)
    db.flush()
    return {
        "classes": len(payload["classes"]),
        "students": len(payload["students"]),
        "pet_progress": len(payload["pet_progress"]),
        "score_events": len(payload["score_events"]),
    }