import re
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.usuario import RolUsuario
from app.infrastructure.models import Base, UsuarioORM
from app.infrastructure.security.password_hasher import hashear_password
from app.main import app
from app.presentation.dependencies import obtener_servicio_correo, obtener_sesion


class CapturadorCorreoFalso:
    def __init__(self) -> None:
        self.enviados: list[dict[str, str]] = []

    def enviar_recuperacion(self, destinatario: str, enlace: str) -> None:
        match = re.search(r"token=([^&\s]+)", enlace)
        token = match.group(1) if match else ""
        self.enviados.append({"destinatario": destinatario, "enlace": enlace, "token": token})


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def capturador_correo() -> CapturadorCorreoFalso:
    return CapturadorCorreoFalso()


@pytest.fixture()
def client(
    db_session: Session, capturador_correo: CapturadorCorreoFalso
) -> Generator[TestClient, None, None]:
    def override_sesion() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[obtener_sesion] = override_sesion
    app.dependency_overrides[obtener_servicio_correo] = lambda: capturador_correo

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def admin_creado(db_session: Session) -> UsuarioORM:
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
