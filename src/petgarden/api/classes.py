"""班级管理路由。"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.deps import get_db
from petgarden.errors import AppError
from petgarden.models import Class
from petgarden.schemas import ClassDeleteIn, ClassIn, ClassPatch
from petgarden.services.roster import class_to_summary, get_class_or_404

router = APIRouter(prefix="/api/classes", tags=["classes"])


@router.get("")
def list_classes(db: Session = Depends(get_db)) -> dict:
    classes = db.scalars(
        select(Class).order_by(Class.sort_order, Class.id)
    ).all()
    return {"classes": [class_to_summary(db, c) for c in classes]}


@router.post("", status_code=201)
def create_class(body: ClassIn, db: Session = Depends(get_db)) -> dict:
    now = utcnow()
    cls = Class(
        name=body.name.strip(),
        grade=body.grade,
        color=body.color or "moss",
        sort_order=0,
        created_at=now,
        updated_at=now,
    )
    db.add(cls)
    db.flush()
    return {"class": class_to_summary(db, cls)}


@router.get("/{class_id}")
def get_class(class_id: int, db: Session = Depends(get_db)) -> dict:
    return {"class": class_to_summary(db, get_class_or_404(db, class_id))}


@router.patch("/{class_id}")
def patch_class(
    class_id: int, body: ClassPatch, db: Session = Depends(get_db)
) -> dict:
    cls = get_class_or_404(db, class_id)
    if body.name is not None:
        cls.name = body.name.strip()
    if body.grade is not None:
        cls.grade = body.grade
    if body.color is not None:
        cls.color = body.color
    if body.sort_order is not None:
        cls.sort_order = body.sort_order
    cls.updated_at = utcnow()
    db.flush()
    return {"class": class_to_summary(db, cls)}


@router.delete("/{class_id}", status_code=204)
def delete_class(
    class_id: int, body: ClassDeleteIn, db: Session = Depends(get_db)
) -> Response:
    cls = get_class_or_404(db, class_id)
    if body.confirm_name != cls.name:
        raise AppError(409, "NAME_MISMATCH", "输入的班级名不匹配，未删除。")
    db.delete(cls)
    db.flush()
    return Response(status_code=204)