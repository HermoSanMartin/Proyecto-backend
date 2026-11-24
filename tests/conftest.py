import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Evita que la configuraci?n de la aplicaci?n dependa del .env personal.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "clave-exclusiva-para-pruebas-automatizadas-locales"


@pytest.fixture(scope="session")
def plantilla_migrada(tmp_path_factory):
    archivo = tmp_path_factory.mktemp("migraciones") / "plantilla.db"
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "DATABASE_URL": f"sqlite:///{archivo.as_posix()}"},
        check=True,
    )
    return archivo


@pytest.fixture
def url_bd_prueba(plantilla_migrada, tmp_path):
    archivo = tmp_path / "galeria.db"
    shutil.copyfile(plantilla_migrada, archivo)
    return f"sqlite:///{archivo.as_posix()}"


@pytest.fixture
def db_session(url_bd_prueba):
    engine = create_engine(url_bd_prueba)
    try:
        with Session(engine) as sesion:
            yield sesion
    finally:
        engine.dispose()
