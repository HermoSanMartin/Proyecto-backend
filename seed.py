"""
Script de poblamiento inicial (seeding) para la base de datos del sistema de galerias.
"""
from sqlalchemy.orm import Session

# Intentamos importar la sesion desde app.database o app.db
try:
    from app.database import SessionLocal
except ImportError:
    from app.db import SessionLocal

from app import models


def poblar_base_de_datos():
    db: Session = SessionLocal()
    try:
        print("[INFO] Iniciando poblamiento de datos de prueba...")

        # 1. Insertar Galerias si la tabla esta vacia
        if hasattr(models, "Galeria") and not db.query(models.Galeria).first():
            galeria1 = models.Galeria(nombre="Galeria Bellas Artes", ubicacion="Santiago Centro")
            galeria2 = models.Galeria(nombre="Galeria Arte Moderno", ubicacion="Providencia")
            db.add_all([galeria1, galeria2])
            db.commit()
            print("[OK] Galerias creadas exitosamente.")

        # 2. Insertar Obras si la tabla esta vacia
        if hasattr(models, "Obra") and not db.query(models.Obra).first():
            obra1 = models.Obra(titulo="Atardecer Urbano", autor="Artista Local", ano=2023)
            obra2 = models.Obra(titulo="Escultura Abstracta", autor="Escultor X", ano=2021)
            db.add_all([obra1, obra2])
            db.commit()
            print("[OK] Obras creadas exitosamente.")

        print("[EXITO] Poblamiento completado con exito.")

    except Exception as error:
        print(f"[ERROR] Error durante el poblamiento: {error}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    poblar_base_de_datos()