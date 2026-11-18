"""
Modulo de reportes y estadisticas para el sistema de galerias.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Import de la sesion de base de datos segun la estructura
try:
    from app.infrastructure.database import get_db
except ImportError:
    try:
        from app.database import get_db
    except ImportError:
        from app.db import get_db

# Import de modelos del dominio
try:
    from app.domain import models
except ImportError:
    from app import models

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/resumen")
def obtener_resumen_estadisticas(db: Session = Depends(get_db)):
    """
    Retorna estadisticas generales acumuladas en el sistema.
    """
    total_obras = db.query(models.Obra).count() if hasattr(models, "Obra") else 0
    total_galerias = db.query(models.Galeria).count() if hasattr(models, "Galeria") else 0
    total_prestamos = db.query(models.Prestamo).count() if hasattr(models, "Prestamo") else 0

    return {
        "total_obras": total_obras,
        "total_galerias": total_galerias,
        "total_prestamos": total_prestamos,
        "estado_sistema": "Operativo"
    }