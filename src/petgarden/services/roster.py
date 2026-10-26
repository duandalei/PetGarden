"""学生花名册服务：CRUD、批量导入、序列化（含派生字段）。"""

import random
import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.domain.pets import (
    NORMAL_SPECIES,
    SPECIES_NAMES,
    divine_unlocked,
    level_from_score,
    mood_from_score,
    stage_from_level,
)
from petgarden.errors import AppError
from petgarden.models import Class, PetProgress, ScoreEvent, Student

_rng = random.SystemRandom()


def progress_map(db: Session, student_id: int) -> dict[str, int]:
    rows = db.scalars(
        select(PetProgress).where(PetProgress.student_id == student_id)
    ).all()
    return {row.species: row.best_level for row in rows}


def ensure_progress(db: Session, student_id: int, species: str) -> PetProgress:
    row = db.get(PetProgress, (student_id, species))
    if row is None:
        now = utcnow()
        row = PetProgress(
            student_id=student_id,
            species=species,
            best_level=1,
            first_reached_at=now,
            last_reached_at=now,
        )
        db.add(row)
    return row


def student_to_dict(db: Session, student: Student) -> dict:
    levels = progress_map(db, student.id)
    unlocked = divine_unlocked(levels)
    level = level_from_score(student.score)
    return {
        "id": student.id,
        "class_id": student.class_id,
        "name": student.name,
        "student_no": student.student_no,
        "seat_no": student.seat_no,
        "score": student.score,
        "level": level,
        "stage": stage_from_level(level),
        "mood": mood_from_score(student.score),
        "score_percent": student.score,
        "species": student.species,
        "species_name": SPECIES_NAMES.get(student.species, student.species),
        "best_level": levels.get(student.species, 1),
        "can_switch_pet": level >= 5,
        "divine_unlocked": unlocked,
        "is_present": bool(student.is_present),
        "last_picked_at": student.last_picked_at,
        "updated_at": student.updated_at,
    }


def event_to_dict(event: ScoreEvent) -> dict:
    return {
        "id": event.id,
        "class_id": event.class_id,
        "student_id": event.student_id,
        "delta": event.delta,
        "score_before": event.score_before,
        "score_after": event.score_after,
        "reason": event.reason,
        "created_at": event.created_at,
        "undone_at": event.undone_at,
    }


def get_class_or_404(db: Session, class_id: int) -> Class:
    cls = db.get(Class, class_id)
    if cls is None:
        raise AppError(404, "CLASS_NOT_FOUND", "班级不存在。")
    return cls


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise AppError(404, "STUDENT_NOT_FOUND", "学生不存在。")
    return student


def class_to_summary(db: Session, cls: Class) -> dict:
    students = db.scalars(
        select(Student).where(Student.class_id == cls.id)
    ).all()
    count = len(students)
    avg = round(sum(s.score for s in students) / count, 1) if count else 0.0
    ordered = sorted(
        students, key=lambda s: (s.seat_no is None, s.seat_no or 0, s.id)
    )
    preview = list(dict.fromkeys(s.species for s in ordered))[:3]
    return {
        "id": cls.id,
        "name": cls.name,
        "grade": cls.grade,
        "color": cls.color,
        "sort_order": cls.sort_order,
        "student_count": count,
        "average_score": avg,
        "preview_species": preview,
        "created_at": cls.created_at,
        "updated_at": cls.updated_at,
    }


def check_duplicate_no(
    db: Session, class_id: int, student_no: str | None, exclude_id: int | None = None
) -> None:
    if not student_no:
        return
    stmt = select(Student).where(
        Student.class_id == class_id, Student.student_no == student_no
    )
    if exclude_id is not None:
        stmt = stmt.where(Student.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise AppError(409, "DUPLICATE_STUDENT_NO", f"学号 {student_no} 在该班已存在。")


def create_student(
    db: Session,
    class_id: int,
    name: str,
    student_no: str | None,
    seat_no: int | None,
    species: str | None,
) -> Student:
    get_class_or_404(db, class_id)
    check_duplicate_no(db, class_id, student_no)
    chosen = species or _rng.choice(NORMAL_SPECIES)
    if chosen not in NORMAL_SPECIES:
        raise AppError(422, "INVALID_SPECIES", "新建学生只能选择普通物种。")
    now = utcnow()
    student = Student(
        class_id=class_id,
        name=name,
        student_no=student_no or None,
        seat_no=seat_no,
        score=0,
        species=chosen,
        is_present=1,
        created_at=now,
        updated_at=now,
    )
    db.add(student)
    db.flush()
    ensure_progress(db, student.id, chosen)
    return student


def sort_students(students: list[Student], sort: str) -> list[Student]:
    if sort == "name":
        return sorted(students, key=lambda s: (s.name, s.id))
    if sort == "score":
        return sorted(students, key=lambda s: (-s.score, s.id))
    return sorted(students, key=lambda s: (s.seat_no is None, s.seat_no or 0, s.id))


_SPLIT_RE = re.compile(r"[,，\t]")
MAX_BULK_LINES = 200


def parse_bulk_text(text: str, existing_nos: set[str]) -> dict:
    lines = text.splitlines()
    if len(lines) > MAX_BULK_LINES:
        raise AppError(422, "VALIDATION_ERROR", f"一次最多导入 {MAX_BULK_LINES} 行。")
    created: list[dict] = []
    skipped: list[dict] = []
    errors: list[dict] = []
    seen_nos: set[str] = set(existing_nos)
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            skipped.append({"line": idx, "reason": "EMPTY_LINE", "text": raw})
            continue
        parts = [p.strip() for p in _SPLIT_RE.split(line)]
        name = parts[0] if parts else ""
        if not name:
            errors.append({"line": idx, "reason": "EMPTY_NAME", "text": raw})
            continue
        if len(name) > 20:
            errors.append({"line": idx, "reason": "NAME_TOO_LONG", "text": raw})
            continue
        student_no = parts[1] if len(parts) > 1 and parts[1] else None
        seat_no: int | None = None
        if len(parts) > 2 and parts[2]:
            try:
                seat_no = int(parts[2])
                if not 1 <= seat_no <= 99:
                    raise ValueError
            except ValueError:
                errors.append({"line": idx, "reason": "INVALID_SEAT", "text": raw})
                continue
        if student_no and len(student_no) > 20:
            errors.append({"line": idx, "reason": "INVALID_STUDENT_NO", "text": raw})
            continue
        if student_no and student_no in seen_nos:
            skipped.append({"line": idx, "reason": "DUPLICATE_STUDENT_NO", "text": raw})
            continue
        if student_no:
            seen_nos.add(student_no)
        created.append(
            {"line": idx, "name": name, "student_no": student_no, "seat_no": seat_no}
        )
    return {"created": created, "skipped": skipped, "errors": errors}


def bulk_create_students(db: Session, class_id: int, text: str) -> dict:
    get_class_or_404(db, class_id)
    existing = db.scalars(
        select(Student.student_no).where(
            Student.class_id == class_id,
            Student.student_no.is_not(None),
            Student.student_no != "",
        )
    ).all()
    parsed = parse_bulk_text(text, set(existing))
    created_students = [
        create_student(db, class_id, item["name"], item["student_no"], item["seat_no"], None)
        for item in parsed["created"]
    ]
    db.flush()
    return {
        "created": [student_to_dict(db, s) for s in created_students],
        "skipped": parsed["skipped"],
        "errors": parsed["errors"],
    }


def latest_event_for_student(db: Session, student_id: int) -> ScoreEvent | None:
    return db.scalar(
        select(ScoreEvent)
        .where(ScoreEvent.student_id == student_id, ScoreEvent.undone_at.is_(None))
        .order_by(ScoreEvent.id.desc())
        .limit(1)
    )


def recent_events(db: Session, student_id: int, limit: int = 5) -> list[ScoreEvent]:
    return list(
        db.scalars(
            select(ScoreEvent)
            .where(ScoreEvent.student_id == student_id)
            .order_by(ScoreEvent.id.desc())
            .limit(limit)
        ).all()
    )


def class_average(db: Session, class_id: int) -> float:
    value = db.scalar(
        select(func.coalesce(func.avg(Student.score), 0.0)).where(
            Student.class_id == class_id
        )
    )
    return round(float(value or 0.0), 1)