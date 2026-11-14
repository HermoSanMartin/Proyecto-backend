from fastapi import FastAPI

from app.presentation.error_handlers import registrar_manejadores
from app.presentation.routers.artistas import router as artistas_router
from app.presentation.routers.exposiciones import router as exposiciones_router
from app.presentation.routers.obra import router as obras_router
from app.presentation.routers.solicitudes import router as solicitudes_router

app = FastAPI(
    title="API de Gestión de Galerías de Arte",
    description="Registro de artistas, obras, exposiciones y préstamos.",
    version="0.1.0",
)

registrar_manejadores(app)
app.include_router(artistas_router)
app.include_router(obras_router)
app.include_router(exposiciones_router)
app.include_router(solicitudes_router)


@app.get("/api/v1/salud", tags=["Sistema"], summary="Verifica que la API está activa")
def verificar_salud():
    return {"estado": "ok"}