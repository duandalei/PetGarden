"""宠物图鉴与换宠路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from petgarden.deps import get_db
from petgarden.domain.pets import LEVEL_THRESHOLDS, SPECIES_CATALOG, STAGE_NAMES
from petgarden.schemas import SwitchPetIn
from petgarden.services.pet_progress import collection_for_student, switch_pet
from petgarden.services.roster import get_student_or_404

router = APIRouter(tags=["pets"])


@router.get("/api/pets")
def pet_catalog() -> dict:
    return {
        "level_thresholds": LEVEL_THRESHOLDS,
        "stage_names": STAGE_NAMES,
        "species": SPECIES_CATALOG,
    }


@router.get("/api/students/{student_id}/collection")
def get_collection(student_id: int, db: Session = Depends(get_db)) -> dict:
    student = get_student_or_404(db, student_id)
    return collection_for_student(db, student)


@router.post("/api/students/{student_id}/switch-pet")
def switch_student_pet(
    student_id: int, body: SwitchPetIn, db: Session = Depends(get_db)
) -> dict:
    student = get_student_or_404(db, student_id)
    return switch_pet(db, student, body.species)