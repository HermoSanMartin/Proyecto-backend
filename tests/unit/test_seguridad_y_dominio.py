from datetime import UTC, date, datetime, timedelta
from unittest.mock import MagicMock

import jwt
import pytest

from app.application.services.artista_service import ArtistaService
from app.application.services.auth_service import AuthService
from app.application.services.obra_service import ObraService
from app.domain.artista import Artista
from app.domain.excepciones import (
    ConflictoDeEstado,
    CuentaBloqueada,
    NoAutenticado,
    RecursoNoEncontrado,
    ReglaDeNegocioViolada,
)
from app.domain.exposicion import EstadoExposicion, Exposicion
from app.domain.obra_de_arte import ObraDeArte
from app.domain.solicitud_prestamo import SolicitudPrestamo
from app.domain.usuario import RolUsuario, Usuario, validar_politica_password
from app.infrastructure.config import configuracion
from app.infrastructure.security.jwt_manager import (
    crear_access_token,
    crear_recovery_token,
    verificar_access_token,
    verificar_recovery_token,
)
from app.infrastructure.security.password_hasher import hashear_password, verificar_password


def test_politica_password_valida_e_invalida():
    validar_politica_password("ClaveSegura2026!")

    with pytest.raises(ReglaDeNegocioViolada) as exc_corta:
        validar_politica_password("Abc12345!")
    assert any("12 caracteres" in d["mensaje"] for d in exc_corta.value.detalles)

    with pytest.raises(ReglaDeNegocioViolada):
        validar_politica_password("solominusculas1234")

    with pytest.raises(ReglaDeNegocioViolada):
        validar_politica_password("SOLOMAYUSCULAS1234")

    with pytest.raises(ReglaDeNegocioViolada):
        validar_politica_password("SinNumerosEnClave!")


def test_hashing_argon2id_y_verificacion():
    secreto = "MiClaveUnica2026!"
    digest = hashear_password(secreto)
    assert digest.startswith("$argon2id$")
    assert digest != secreto
    assert verificar_password(secreto, digest) is True
    assert verificar_password("ClaveIncorrecta2026!", digest) is False
    assert verificar_password(secreto, "hash-corrupto") is False


def test_jwt_access_y_recovery_validacion_y_proposito():
    access = crear_access_token(usuario_id=7, rol="admin", token_version=2)
    payload_access = verificar_access_token(access)
    assert payload_access["sub"] == "7"
    assert payload_access["rol"] == "admin"
    assert payload_access["ver"] == 2
    assert payload_access["type"] == "access"

    recovery, _ = crear_recovery_token(usuario_id=7, jti="jti-unico-123")
    payload_rec = verificar_recovery_token(recovery)
    assert payload_rec["sub"] == "7"
    assert payload_rec["jti"] == "jti-unico-123"
    assert payload_rec["type"] == "recovery"

    with pytest.raises(NoAutenticado):
        verificar_access_token(recovery)
    with pytest.raises(NoAutenticado):
        verificar_recovery_token(access)

    with pytest.raises(NoAutenticado):
        verificar_access_token(access + "tampered")

    expirado = jwt.encode(
        {
            "sub": "7",
            "rol": "admin",
            "ver": 2,
            "type": "access",
            "exp": int((datetime.now(UTC) - timedelta(minutes=5)).timestamp()),
        },
        configuracion.jwt_secret_key,
        algorithm=configuracion.jwt_algorithm,
    )
    with pytest.raises(NoAutenticado):
        verificar_access_token(expirado)


def test_auth_service_bloqueo_por_intentos_fallidos():
    repo = MagicMock()
    correo = MagicMock()
    usuario = Usuario(
        id=1,
        nombre="Ana",
        email="ana@galeria.cl",
        password_hash=hashear_password("ClaveValida2026!"),
        rol=RolUsuario.USUARIO,
        activo=True,
    )
    repo.obtener_por_email.return_value = usuario
    repo.actualizar.side_effect = lambda u: u

    servicio = AuthService(repo, correo)

    for _ in range(5):
        with pytest.raises(NoAutenticado):
            servicio.iniciar_sesion("ana@galeria.cl", "ClaveErronea2026!")

    assert usuario.intentos_fallidos == 5
    assert usuario.bloqueado_hasta is not None

    with pytest.raises(CuentaBloqueada):
        servicio.iniciar_sesion("ana@galeria.cl", "ClaveValida2026!")

    usuario.bloqueado_hasta = datetime.now(UTC) - timedelta(minutes=1)
    _, access, refresh = servicio.iniciar_sesion("ana@galeria.cl", "ClaveValida2026!")
    assert access
    assert refresh
    assert usuario.intentos_fallidos == 0


def test_auth_service_deteccion_reutilizacion_refresh():
    repo = MagicMock()
    servicio = AuthService(repo, MagicMock())

    registro_revocado = MagicMock()
    registro_revocado.revocado = True
    registro_revocado.familia_id = "familia-abc-123"
    repo.obtener_refresh_por_hash.return_value = registro_revocado

    with pytest.raises(NoAutenticado) as exc:
        servicio.renovar_tokens("token-ya-rotado-previamente")

    assert "Reutilizacion" in exc.value.mensaje
    repo.revocar_familia_refresh.assert_called_once_with("familia-abc-123")


def test_auth_service_recuperacion_rechaza_segundo_uso():
    repo = MagicMock()
    servicio = AuthService(repo, MagicMock())
    token, _ = crear_recovery_token(usuario_id=4, jti="jti-consumido")

    registro = MagicMock()
    registro.usuario_id = 4
    registro.usado = True
    registro.expira_en = datetime.now(UTC) + timedelta(minutes=10)
    repo.obtener_token_recuperacion_por_jti.return_value = registro

    with pytest.raises(NoAutenticado) as exc:
        servicio.restablecer_password(token, "NuevaClaveSegura2026!")
    assert "ya fue utilizado" in exc.value.mensaje


def test_dominio_reglas_exposicion_y_solicitud():
    with pytest.raises(ReglaDeNegocioViolada):
        Exposicion(
            nombre_evento="Expo Invalida",
            lugar="Temuco",
            fecha_inicio=date(2026, 12, 20),
            fecha_fin=date(2026, 12, 10),
            estado=EstadoExposicion.PLANIFICADA,
        )

    with pytest.raises(ReglaDeNegocioViolada):
        SolicitudPrestamo(
            obra_id=1,
            exposicion_id=1,
            dias_prestamo=0,
        )


def test_servicios_negocio_validaciones_unitarias():
    repo_artista = MagicMock()
    repo_artista.obtener_por_email.return_value = Artista(
        id=1,
        nombre_artistico="Existente",
        email="dup@galeria.cl",
        nacionalidad="Chilena",
        biografia="Biografia de prueba.",
    )
    serv_artista = ArtistaService(repo_artista)
    with pytest.raises(ConflictoDeEstado):
        serv_artista.crear(
            Artista(
                nombre_artistico="Nuevo",
                email="dup@galeria.cl",
                nacionalidad="Chilena",
                biografia="Biografia de prueba.",
            )
        )

    repo_artista.obtener_por_id.return_value = None
    serv_obra = ObraService(MagicMock(), repo_artista)
    with pytest.raises(RecursoNoEncontrado):
        serv_obra.crear(
            ObraDeArte(
                titulo="Sin Artista",
                precio_estimado=1000,
                anio_creacion=2020,
                estilo="Oleo",
                artista_id=999,
            )
        )
