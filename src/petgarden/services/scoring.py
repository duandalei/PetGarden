"""积分与撤销服务。"""

from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.domain.pets import level_from_score
from petgarden.domain.scoring import ScoreAtLimitError, apply_delta
from petgarden.errors import AppError
from petgarden.models import ScoreEvent, Student
from petgarden.services.pet_progress import sync_progress
from petgarden.services.roster import event_to_dict, latest_event_for_student, student_to_dict


def apply_score(db: Session, student: Student, delta: int, reason: str | None) -> dict:
    try:
        new_score = apply_delta(student.score, delta)
    except ScoreAtLimitError:
        if delta > 0:
            message = "已经满 100 分啦，可以准备换一位新伙伴了。"
        else:
            message = "现在是 0 分，先给一个鼓励吧。"
        raise AppError(409, "SCORE_AT_LIMIT", message) from None
    except ValueError as exc:
        raise AppError(422, "VALIDATION_ERROR", str(exc)) from None

    level_before = level_from_score(student.score)
    level_after = level_from_score(new_score)

    event = ScoreEvent(
        class_id=student.class_id,
        student_id=student.id,
        delta=delta,
        score_before=student.score,
        score_after=new_score,
        reason=reason or None,
        created_at=utcnow(),
        undone_at=None,
    )
    db.add(event)
    student.score = new_score
    student.updated_at = utcnow()
    db.flush()
    sync_progress(db, student)
    db.flush()
    db.refresh(event)

    return {
        "student": student_to_dict(db, student),
        "event": event_to_dict(event),
        "level_up": level_after > level_before,
        "stage_changed": level_after != level_before,
        "can_undo": True,
    }


def undo_event(db: Session, event_id: int) -> dict:
    event = db.get(ScoreEvent, event_id)
    if event is None:
        raise AppError(404, "EVENT_NOT_FOUND", "积分事件不存在。")
    if event.undone_at is not None:
        raise AppError(409, "EVENT_ALREADY_UNDONE", "这条记录已经撤销过了。")
    student = db.get(Student, event.student_id)
    if student is None:
        raise AppError(404, "STUDENT_NOT_FOUND", "学生不存在。")
    latest = latest_event_for_student(db, student.id)
    if latest is None or latest.id != event.id or student.score != event.score_after:
        raise AppError(
            409, "EVENT_NOT_LATEST", "只能撤销该学生最新的一次加分或减分。"
        )
    student.score = event.score_before
    student.updated_at = utcnow()
    event.undone_at = utcnow()
    db.flush()
    return {"student": student_to_dict(db, student), "event": event_to_dict(event)}