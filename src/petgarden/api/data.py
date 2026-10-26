"""数据导出/导入路由。"""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from petgarden.db import utcnow
from petgarden.deps import get_db
from petgarden.errors import AppError
from petgarden.schemas import ImportIn
from petgarden.services.backup import (
    MAX_IMPORT_BYTES,
    build_export,
    import_backup,
    validate_backup,
    write_pre_import_backup,
)

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/export")
def export_data(db: Session = Depends(get_db)) -> JSONResponse:
    payload = build_export(db)
    stamp = utcnow().replace(":", "").replace("-", "").replace("T", "-").rstrip("Z")
    filename = f"petgarden-backup-{stamp}.json"
    return JSONResponse(
        payload,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("/import")
def import_data(
    body: ImportIn, request: Request, db: Session = Depends(get_db)
) -> dict:
    if body.confirm != "REPLACE":
        raise AppError(
            400, "IMPORT_CONFIRM_REQUIRED", "请输入 REPLACE 以确认替换全部数据。"
        )
    raw = json.dumps(body.backup, ensure_ascii=False)
    if len(raw.encode("utf-8")) > MAX_IMPORT_BYTES:
        raise AppError(422, "IMPORT_INVALID", "备份文件超过 5MB 限制。")
    payload = validate_backup(body.backup)
    write_pre_import_backup(db, request.app.state.settings.backups_dir)
    counts = import_backup(db, payload)
    return {"ok": True, "counts": counts}
