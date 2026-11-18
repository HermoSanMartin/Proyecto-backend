from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.excepciones import ConflictoDeEstado, ErrorDeDominio, RecursoNoEncontrado


def _respuesta(estado: int, codigo: str, mensaje: str, detalles: list | None = None):
    return JSONResponse(
        status_code=estado,
        content={"error": {"code": codigo, "message": mensaje, "details": detalles or []}},
    )


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDeDominio)
    async def manejar_error_de_dominio(request, exc: ErrorDeDominio):
        if isinstance(exc, RecursoNoEncontrado):
            estado = 404
        elif isinstance(exc, ConflictoDeEstado):
            estado = 409
        else:
            estado = 400
        return _respuesta(estado, exc.codigo, exc.mensaje, exc.detalles)

    @app.exception_handler(RequestValidationError)
    async def manejar_validacion(request, exc: RequestValidationError):
        detalles = [
            {
                "campo": ".".join(str(p) for p in e["loc"] if p != "body"),
                "mensaje": e["msg"],
            }
            for e in exc.errors()
        ]
        return _respuesta(422, "VALIDATION_ERROR", "Los datos enviados no son válidos", detalles)

    @app.exception_handler(StarletteHTTPException)
    async def manejar_http(request, exc: StarletteHTTPException):
        return _respuesta(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(Exception)
    async def manejar_inesperado(request, exc: Exception):
        return _respuesta(500, "INTERNAL_ERROR", "Ocurrió un error interno")