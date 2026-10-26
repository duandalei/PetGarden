"""随机点名与大屏数据路由。"""

import random

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.deps import get_db
from petgarden.domain.rollcall import NoStudentsError, RollcallEntry, choose
from petgarden.errors import AppError
from petgarden.models import Student
from petgarden.schemas import RollcallIn
from petgarden.services.roster import (
    class_to_summary,
    get_class_or_404,
    sort_students,
    student_to_dict,
)

router = APIRouter(prefix="/api/classes/{class_id}", tags=["rollcall"])

_rng = random.SystemRandom()


@router.post("/rollcall")
def rollcall(class_id: int, body: RollcallIn, db: Session = Depends(get_db)) -> dict:
    get_class_or_404(db, class_id)
    students = list(
        db.scalars(select(Student).where(Student.class_id == class_id)).all()
    )
    candidates = [s for s in students if s.is_present] if body.exclude_absent else students
    if not candidates:
        raise AppError(409, "NO_STUDENTS", "这个班级暂时没有可以点名的学生。")
    entries = [RollcallEntry(id=s.id, last_picked_at=s.last_picked_at) for s in candidates]
    last = max(
        (s for s in candidates if s.last_picked_at),
        key=lambda s: s.last_picked_at or "",
        default=None,
    )
    last_picked_id = last.id if last else None
    try:
        picked = choose(entries, body.mode, last_picked_id, _rng)
    except NoStudentsError:
        raise AppError(409, "NO_STUDENTS", "这个班级暂时没有可以点名的学生。") from None
    student = db.get(Student, picked.id)
    assert student is not None
    student.last_picked_at = utcnow()
    student.updated_at = utcnow()
    db.flush()
    pool_size = len(entries) if body.mode == "random" else max(1, -(-len(entries) // 3))
    return {
        "student": student_to_dict(db, student),
        "pool_size": pool_size,
        "mode": body.mode,
    }


@router.get("/display")
def display(class_id: int, db: Session = Depends(get_db)) -> dict:
    cls = get_class_or_404(db, class_id)
    students = list(
        db.scalars(select(Student).where(Student.class_id == class_id)).all()
    )
    students = sort_students(students, "seat")
    return {
        "class": class_to_summary(db, cls),
        "students": [student_to_dict(db, s) for s in students],
        "server_time": utcnow(),
    }