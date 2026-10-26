"""积分与撤销路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from petgarden.deps import get_db
from petgarden.schemas import ScoreIn
from petgarden.services.roster import get_student_or_404
from petgarden.services.scoring import apply_score, undo_event

router = APIRouter(tags=["scoring"])


@router.post("/api/students/{student_id}/score")
def score_student(
    student_id: int, body: ScoreIn, db: Session = Depends(get_db)
) -> dict:
    student = get_student_or_404(db, student_id)
    return apply_score(db, student, body.delta, body.reason)


@router.post("/api/score-events/{event_id}/undo")
def undo_score_event(event_id: int, db: Session = Depends(get_db)) -> dict:
    return undo_event(db, event_id)