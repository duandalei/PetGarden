"""学生管理路由。"""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.deps import get_db
from petgarden.models import Student
from petgarden.schemas import BulkIn, StudentIn, StudentPatch
from petgarden.services.roster import (
    bulk_create_students,
    check_duplicate_no,
    create_student,
    event_to_dict,
    get_class_or_404,
    get_student_or_404,
    parse_bulk_text,
    recent_events,
    sort_students,
    student_to_dict,
)

router = APIRouter(tags=["students"])


@router.get("/api/classes/{class_id}/students")
def list_students(
    class_id: int,
    sort: str = Query(default="seat", pattern="^(seat|name|score)$"),
    q: str = Query(default=""),
    db: Session = Depends(get_db),
) -> dict:
    get_class_or_404(db, class_id)
    students = list(
        db.scalars(select(Student).where(Student.class_id == class_id)).all()
    )
    keyword = q.strip()
    if keyword:
        students = [
            s
            for s in students
            if keyword in s.name or (s.student_no and keyword in s.student_no)
        ]
    students = sort_students(students, sort)
    return {"students": [student_to_dict(db, s) for s in students]}


@router.post("/api/classes/{class_id}/students", status_code=201)
def add_student(
    class_id: int, body: StudentIn, db: Session = Depends(get_db)
) -> dict:
    student = create_student(
        db,
        class_id,
        body.name.strip(),
        body.student_no,
        body.seat_no,
        body.species,
    )
    db.flush()
    return {"student": student_to_dict(db, student)}


@router.post("/api/classes/{class_id}/students/bulk")
def bulk_students(
    class_id: int, body: BulkIn, db: Session = Depends(get_db)
) -> dict:
    get_class_or_404(db, class_id)
    if body.preview:
        from sqlalchemy import select as sa_select

        existing = db.scalars(
            sa_select(Student.student_no).where(
                Student.class_id == class_id,
                Student.student_no.is_not(None),
                Student.student_no != "",
            )
        ).all()
        parsed = parse_bulk_text(body.text, set(existing))
        return {"preview": True, **parsed}
    result = bulk_create_students(db, class_id, body.text)
    return {"preview": False, **result}


@router.get("/api/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)) -> dict:
    student = get_student_or_404(db, student_id)
    events = recent_events(db, student.id, limit=5)
    return {
        "student": student_to_dict(db, student),
        "recent_events": [event_to_dict(e) for e in events],
    }


@router.patch("/api/students/{student_id}")
def patch_student(
    student_id: int, body: StudentPatch, db: Session = Depends(get_db)
) -> dict:
    student = get_student_or_404(db, student_id)
    if body.name is not None:
        student.name = body.name.strip()
    if body.student_no is not None:
        no = body.student_no.strip() or None
        check_duplicate_no(db, student.class_id, no, exclude_id=student.id)
        student.student_no = no
    if body.seat_no is not None:
        student.seat_no = body.seat_no
    if body.is_present is not None:
        student.is_present = 1 if body.is_present else 0
    student.updated_at = utcnow()
    db.flush()
    return {"student": student_to_dict(db, student)}


@router.delete("/api/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)) -> Response:
    student = get_student_or_404(db, student_id)
    db.delete(student)
    db.flush()
    return Response(status_code=204)