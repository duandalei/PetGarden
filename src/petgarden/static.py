"""生产模式静态资源与 SPA fallback。"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

_BUILD_HINT = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>PetGarden</title></head><body style="font-family:sans-serif;padding:48px">
<h1>前端尚未构建</h1>
<p>请先在项目目录执行：</p>
<pre>cd frontend\nnpm install\nnpm run build</pre>
<p>然后重新启动服务。</p></body></html>"""


def mount_static(app: FastAPI, dist_dir: Path) -> None:
    assets_dir = dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="assets",
        )

    @app.get("/{full_path:path}", include_in_schema=False, response_model=None)
    def spa_fallback(full_path: str) -> Response:
        if full_path.startswith("api/") or full_path == "api":
            return JSONResponse(
                status_code=404,
                content={"error": {"code": "NOT_FOUND", "message": "接口不存在"}},
            )
        if not dist_dir.is_dir():
            return HTMLResponse(_BUILD_HINT, status_code=200)
        candidate = dist_dir / full_path
        if full_path and candidate.is_file() and candidate.resolve().is_relative_to(
            dist_dir.resolve()
        ):
            return FileResponse(candidate)
        index = dist_dir / "index.html"
        if index.is_file():
            return FileResponse(index)
        return HTMLResponse(_BUILD_HINT, status_code=200)