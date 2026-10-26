"""设置路由。"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from petgarden.db import get_setting, set_setting
from petgarden.deps import get_db
from petgarden.schemas import SettingsPatch

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _settings_payload(request: Request, db: Session) -> dict:
    settings = request.app.state.settings
    return {
        "motion_pref": get_setting(db, "motion_pref", "system"),
        "display_sort": get_setting(db, "display_sort", "seat"),
        "version": settings.version,
        "build_time": settings.build_time,
        "data_dir": str(settings.data_dir),
    }


@router.get("")
def get_settings(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    return _settings_payload(request, db)


@router.patch("")
def patch_settings(
    body: SettingsPatch,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    if body.motion_pref is not None:
        set_setting(db, "motion_pref", body.motion_pref)
    if body.display_sort is not None:
        set_setting(db, "display_sort", body.display_sort)
    db.flush()
    return _settings_payload(request, db)