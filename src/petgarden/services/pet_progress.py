"""宠物进度同步与换宠服务。"""

from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.domain.pets import (
    DIVINE_SPECIES,
    SPECIES_NAMES,
    can_switch_pet,
    divine_unlocked,
    level_from_score,
)
from petgarden.errors import AppError
from petgarden.models import Student
from petgarden.services.roster import (
    ensure_progress,
    progress_map,
    student_to_dict,
)


def sync_progress(db: Session, student: Student) -> None:
    """把当前物种的 best_level 同步到历史最高（只升不降）。"""
    progress = ensure_progress(db, student.id, student.species)
    level = level_from_score(student.score)
    if level > progress.best_level:
        progress.best_level = level
        progress.last_reached_at = utcnow()


def switch_pet(db: Session, student: Student, target_species: str) -> dict:
    levels = progress_map(db, student.id)
    unlocked = divine_unlocked(levels)
    ok, code = can_switch_pet(
        student.score, student.species, target_species, unlocked
    )
    if not ok:
        if code == "INVALID_SPECIES":
            raise AppError(422, "INVALID_SPECIES", "不支持的宠物物种。")
        if code == "SAME_SPECIES":
            raise AppError(409, "SAME_SPECIES", "已经是这位伙伴啦。")
        if code == "PET_SWITCH_NOT_READY":
            raise AppError(
                409, "PET_SWITCH_NOT_READY", "当前宠物达到 L5 满级后才能换宠。"
            )
        if code == "DIVINE_LOCKED":
            raise AppError(
                403, "DIVINE_LOCKED", "任意一只普通宠物达到 L5，就能解锁神兽。"
            )
    previous = student.species
    previous_best = levels.get(previous, level_from_score(student.score))
    student.species = target_species
    student.score = 0
    student.updated_at = utcnow()
    db.flush()
    ensure_progress(db, student.id, target_species)
    db.flush()
    return {
        "student": student_to_dict(db, student),
        "previous_species": previous,
        "previous_species_name": SPECIES_NAMES.get(previous, previous),
        "previous_best_level": previous_best,
        "graduated": previous_best >= 5,
        "message": "满级毕业！新伙伴已经入住。",
    }


def collection_for_student(db: Session, student: Student) -> dict:
    levels = progress_map(db, student.id)
    unlocked = divine_unlocked(levels)
    items = []
    from petgarden.domain.pets import SPECIES_CATALOG

    for entry in SPECIES_CATALOG:
        sp = entry["id"]
        best = levels.get(sp, 0)
        item_unlocked = unlocked if sp in DIVINE_SPECIES else True
        items.append(
            {
                "species": sp,
                "name": entry["name"],
                "type": entry["type"],
                "best_level": best,
                "is_current": sp == student.species,
                "unlocked": item_unlocked,
            }
        )
    return {
        "student_id": student.id,
        "current_species": student.species,
        "can_switch_pet": level_from_score(student.score) >= 5,
        "divine_unlocked": unlocked,
        "items": items,
    }