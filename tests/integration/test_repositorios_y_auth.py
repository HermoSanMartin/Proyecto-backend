import re
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.exposicion_service import ExposicionService
from app.application.services.obra_service import ObraService
from app.application.services.solicitud_service import SolicitudService
from app.domain.artista import Artista
from app.domain.excepciones import ConflictoDeEstado, NoAutenticado, ReglaDeNegocioViolada
from app.domain.exposicion import EstadoExposicion, Exposicion
from app.domain.obra_de_arte import ObraDeArte
from app.domain.solicitud_prestamo import EstadoSolicitud, SolicitudPrestamo
from app.infrastructure.repositories.artista_repository import ArtistaRepository
from app.infrastructure.repositories.exposicion_repository import ExposicionRepository
from app.infrastructure.repositories.obra_repository import ObraRepository
from app.infrastructure.repositories.solicitud_repository import SolicitudRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.jwt_manager import crear_recovery_token
from app.infrastructure.security.password_hasher import hashear_password, verificar_password


class CapturadorCorreoFalso:
    def __init__(self) -> None:
        self.enviados: list[dict[str, str]] = []

    def enviar_recuperacion(self, destinatario: str, enlace: str) -> None:
        match = re.search(r"token=([^&\s]+)", enlace)
        token = match.group(1) if match else ""
        self.enviados.append({"destinatario": destinatario, "enlace": enlace, "token": token})


def test_integracion_usuario_repository_y_unicidad(db_session: Session):
    repo = UsuarioRepository(db_session)
    servicio = AuthService(repo, CapturadorCorreoFalso())

    creado = servicio.registrar("Camila Soto", "Camila@Galeria.CL", "ClaveSegura2026!")
    assert creado.id is not None
    assert creado.email == "camila@galeria.cl"

    recuperado = repo.obtener_por_email("camila@galeria.cl")
    assert recuperado is not None
    assert recuperado.id == creado.id

    with pytest.raises(ConflictoDeEstado):
        servicio.registrar("Otra Camila", "camila@galeria.cl", "OtraClaveSegura2026!")


def test_integracion_rotacion_refresh_y_revocacion_familia(db_session: Session):
    repo = UsuarioRepository(db_session)
    servicio = AuthService(repo, CapturadorCorreoFalso())
    servicio.registrar("Diego R.", "diego@galeria.cl", "ClaveSegura2026!")

    _, access_1, refresh_1 = servicio.iniciar_sesion("diego@galeria.cl", "ClaveSegura2026!")
    assert access_1

    access_2, refresh_2 = servicio.renovar_tokens(refresh_1)
    assert access_2
    assert refresh_2 != refresh_1

    with pytest.raises(NoAutenticado):
        servicio.renovar_tokens(refresh_1)

    with pytest.raises(NoAutenticado):
        servicio.renovar_tokens(refresh_2)


def test_integracion_recuperacion_consumo_e_invalidacion_sesiones(db_session: Session):
    repo = UsuarioRepository(db_session)
    correo = CapturadorCorreoFalso()
    servicio = AuthService(repo, correo)
    usuario = servicio.registrar("Elena M.", "elena@galeria.cl", "ClaveInicial2026!")

    _, access_previo, refresh_previo = servicio.iniciar_sesion(
        "elena@galeria.cl", "ClaveInicial2026!"
    )
    assert servicio.obtener_usuario_desde_access_token(access_previo).id == usuario.id

    token_recup = servicio.solicitar_recuperacion("elena@galeria.cl")
    assert token_recup is not None
    assert len(correo.enviados) == 1

    servicio.restablecer_password(token_recup, "ClaveNuevaSegura2026!")

    with pytest.raises(NoAutenticado):
        servicio.restablecer_password(token_recup, "OtraClaveSegura2026!")

    with pytest.raises(NoAutenticado):
        servicio.obtener_usuario_desde_access_token(access_previo)
    with pytest.raises(NoAutenticado):
        servicio.renovar_tokens(refresh_previo)

    with pytest.raises(NoAutenticado):
        servicio.iniciar_sesion("elena@galeria.cl", "ClaveInicial2026!")
    _, access_nuevo, _ = servicio.iniciar_sesion("elena@galeria.cl", "ClaveNuevaSegura2026!")
    assert access_nuevo


def test_integracion_recovery_token_expirado_en_bd(db_session: Session):
    repo = UsuarioRepository(db_session)
    servicio = AuthService(repo, CapturadorCorreoFalso())
    usuario = servicio.registrar("Mario P.", "mario@galeria.cl", "ClaveInicial2026!")

    token, _ = crear_recovery_token(usuario.id, "jti-vencido-bd")
    repo.guardar_token_recuperacion(
        usuario_id=usuario.id,
        jti="jti-vencido-bd",
        expira_en=datetime.now(UTC) - timedelta(minutes=2),
    )

    with pytest.raises(NoAutenticado):
        servicio.restablecer_password(token, "NuevaClaveValida2026!")


def test_integracion_obras_filtro_orden_y_paginacion(db_session: Session):
    repo_artista = ArtistaRepository(db_session)
    repo_obra = ObraRepository(db_session)
    serv_obra = ObraService(repo_obra, repo_artista)

    artista = repo_artista.crear(
        Artista(
            nombre_artistico="Vicente Huidobro",
            email="vicente@galeria.cl",
            nacionalidad="Chilena",
            biografia="Biografia de prueba.",
        )
    )
    serv_obra.crear(
        ObraDeArte(
            titulo="Altazor",
            precio_estimado=5000,
            anio_creacion=1931,
            estilo="Creacionismo",
            artista_id=artista.id,
        )
    )
    serv_obra.crear(
        ObraDeArte(
            titulo="Ecuatorial",
            precio_estimado=3000,
            anio_creacion=1918,
            estilo="Creacionismo",
            artista_id=artista.id,
        )
    )
    serv_obra.crear(
        ObraDeArte(
            titulo="Paisaje Sur",
            precio_estimado=2000,
            anio_creacion=1925,
            estilo="Realismo",
            artista_id=artista.id,
        )
    )

    items, total, total_paginas = serv_obra.listar(
        estilo="Creacionismo",
        ordenar_por="precio_estimado",
        direccion="desc",
        pagina=1,
        limite=1,
    )
    assert total == 2
    assert total_paginas == 2
    assert len(items) == 1
    assert items[0].titulo == "Altazor"


def test_integracion_solicitud_prestamo_aprobacion_y_disponibilidad(db_session: Session):
    repo_artista = ArtistaRepository(db_session)
    repo_obra = ObraRepository(db_session)
    repo_expo = ExposicionRepository(db_session)
    repo_sol = SolicitudRepository(db_session)

    serv_expo = ExposicionService(repo_expo)
    serv_sol = SolicitudService(repo_sol, repo_obra, repo_expo)

    artista = repo_artista.crear(
        Artista(
            nombre_artistico="Violeta Parra",
            email="violeta@galeria.cl",
            nacionalidad="Chilena",
            biografia="Biografia de prueba.",
        )
    )
    obra = repo_obra.crear(
        ObraDeArte(
            titulo="El Gavilan",
            precio_estimado=12000,
            anio_creacion=1964,
            estilo="Arpillera",
            disponible=True,
            artista_id=artista.id,
        )
    )
    expo = serv_expo.crear(
        Exposicion(
            nombre_evento="Muestra Nacional",
            lugar="Santiago",
            fecha_inicio=date(2026, 12, 1),
            fecha_fin=date(2026, 12, 20),
            estado=EstadoExposicion.PLANIFICADA,
        )
    )

    sol = serv_sol.crear(
        SolicitudPrestamo(
            obra_id=obra.id,
            exposicion_id=expo.id,
            dias_prestamo=10,
        )
    )
    assert sol.estado_solicitud == EstadoSolicitud.PENDIENTE

    aprobada = serv_sol.aprobar(sol.id)
    assert aprobada.estado_solicitud == EstadoSolicitud.APROBADO
    assert repo_obra.obtener_por_id(obra.id).disponible is False

    with pytest.raises(ReglaDeNegocioViolada):
        serv_sol.crear(
            SolicitudPrestamo(
                obra_id=obra.id,
                exposicion_id=expo.id,
                dias_prestamo=5,
            )
        )
    assert verificar_password("x", hashear_password("x")) is True
