from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import configuracion
from app.presentation.error_handlers import registrar_manejadores
from app.presentation.routers.artistas import router as artistas_router
from app.presentation.routers.auth import router as auth_router
from app.presentation.routers.exposiciones import router as exposiciones_router
from app.presentation.routers.obra import router as obras_router
from app.presentation.routers.solicitudes import router as solicitudes_router
from app.presentation.schemas.respuesta import RespuestaError

app = FastAPI(
    responses={422: {"model": RespuestaError, "description": "Datos de entrada invalidos"}},
    title="API de Gestion de Galerias de Arte",
    description="Registro de artistas, obras, exposiciones, prestamos y seguridad JWT.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.lista_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

registrar_manejadores(app)
app.include_router(auth_router)
app.include_router(artistas_router)
app.include_router(obras_router)
app.include_router(exposiciones_router)
app.include_router(solicitudes_router)


@app.get("/api/v1/salud", tags=["Sistema"], summary="Verifica que la API esta activa")
def verificar_salud():
    return {"estado": "ok"}
