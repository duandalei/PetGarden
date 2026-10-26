from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        parts: list[str] = []
        for err in exc.errors()[:3]:
            loc = ".".join(
                str(p) for p in err.get("loc", []) if p not in ("body", "query", "path")
            )
            parts.append(f"{loc or '参数'}: {err.get('msg', '')}")
        message = "；".join(parts) or "参数校验失败"
        return JSONResponse(
            status_code=422, content=error_body("VALIDATION_ERROR", message)
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse | PlainTextResponse:
        if request.url.path.startswith("/api"):
            code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
            message = "接口不存在" if exc.status_code == 404 else "请求失败"
            return JSONResponse(
                status_code=exc.status_code, content=error_body(code, message)
            )
        return PlainTextResponse("Not Found", status_code=exc.status_code)