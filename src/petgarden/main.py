"""FastAPI 应用工厂。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from petgarden.api import classes, data, pets, rollcall, scoring, students
from petgarden.api import settings as settings_api
from petgarden.config import Settings
from petgarden.db import create_engine_for, init_db, make_session_factory
from petgarden.errors import register_error_handlers
from petgarden.static import mount_static

_DEV_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}
_WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.backups_dir.mkdir(parents=True, exist_ok=True)

    engine = create_engine_for(settings.db_path)
    init_db(engine)

    app = FastAPI(
        title="PetGarden",
        version=settings.version,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings = settings
    app.state.session_factory = make_session_factory(engine)


    register_error_handlers(app)

    @app.middleware("http")
    async def origin_guard(request: Request, call_next):  # noqa: ANN001, ANN202
        if request.method in _WRITE_METHODS:
            origin = request.headers.get("origin")
            if origin:
                host = request.headers.get("host", "")
                allowed = {f"http://{host}", f"https://{host}", *_DEV_ORIGINS}
                if origin not in allowed:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": {
                                "code": "FORBIDDEN",
                                "message": "跨站请求被拒绝。",
                            }
                        },
                    )
        return await call_next(request)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "version": settings.version}


    app.include_router(classes.router)
    app.include_router(students.router)
    app.include_router(scoring.router)
    app.include_router(pets.router)
    app.include_router(rollcall.router)
    app.include_router(data.router)
    app.include_router(settings_api.router)

    mount_static(app, settings.frontend_dist)
    return app


app = create_app()