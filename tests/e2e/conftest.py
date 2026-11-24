import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from app.domain.usuario import RolUsuario
from app.infrastructure.models import UsuarioORM
from app.infrastructure.security.password_hasher import hashear_password


@pytest.fixture
def admin_creado(db_session):
    admin = UsuarioORM(
        nombre="Curador Jefe",
        email="admin.test@galeria.cl",
        password_hash=hashear_password("AdminClaveSegura2026!"),
        rol=RolUsuario.ADMIN.value,
        activo=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def mailpit():
    with httpx.Client(base_url="http://127.0.0.1:8025", trust_env=False) as cliente:
        yield cliente


@pytest.fixture
def client(url_bd_prueba, tmp_path):
    puerto = tmp_path / "puerto"
    proceso = subprocess.Popen(
        [sys.executable, "-m", "tests.e2e.servidor", str(puerto)],
        cwd=Path(__file__).resolve().parents[2],
        env={
            **os.environ,
            "DATABASE_URL": url_bd_prueba,
            "SMTP_HOST": "127.0.0.1",
            "SMTP_PORT": "1025",
            "COOKIE_SECURE": "false",
        },
        stdin=subprocess.PIPE,
    )
    try:
        with httpx.Client(trust_env=False) as cliente:
            limite = time.monotonic() + 30
            while time.monotonic() < limite:
                if proceso.poll() is not None:
                    pytest.fail(f"Uvicorn termino durante el inicio: {proceso.returncode}")
                if puerto.exists() and (numero := puerto.read_text().strip()):
                    cliente.base_url = f"http://127.0.0.1:{numero}"
                    try:
                        if cliente.get("/api/v1/salud", timeout=1).is_success:
                            break
                    except httpx.TransportError:
                        pass
                time.sleep(0.1)
            else:
                pytest.fail("La API de prueba no respondio en 30 segundos")
            yield cliente
    finally:
        proceso.stdin.close()
        try:
            proceso.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proceso.kill()
            proceso.wait()
            pytest.fail("La API de prueba no se detuvo correctamente")
