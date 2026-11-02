from fastapi import FastAPI
from app.presentation.routers.reportes import router as reportes_router

app = FastAPI(
    title="Api de gestion de galerias de arte",
    description="Registro de artistas, obras, exposiciones y prestamos",
    version="0.1.0",
)

# Registramos el nuevo modulo sin alterar nada de lo anterior
app.include_router(reportes_router)


@app.get(
    "/api/v1/prueba_de_dependencias",
    tags=["sistema"],
    summary="Verifica que la api este activa",
)
def verificar_dependencias():
    return {"estado": "ok"}