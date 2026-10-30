from fastapi import FastAPI

app = FastAPI(
    title = "Api de gestion de galerias de arte",
    description = "Registro de artistas, obras, exposiciones y prestamos",
    version = "0.1.0",
)


@app.get(
    "/api/v1/prueba_de_dependencias",
    tags=["sistema"],
    summary="Verifica que la api este activa",

)

def verificar_dependencias():
    return{ "estado": "ok" }