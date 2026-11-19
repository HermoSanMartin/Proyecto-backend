from fastapi import APIRouter, Depends, status

from app.application.services.solicitud_service import SolicitudService
from app.domain.solicitud_prestamo import SolicitudPrestamo
from app.domain.usuario import Usuario
from app.presentation.dependencies import (
    exigir_admin,
    obtener_servicio_solicitud,
    obtener_usuario_actual,
)
from app.presentation.schemas.solicitud_schema import SolicitudCrear, SolicitudRespuesta

router = APIRouter(prefix="/api/v1/solicitudes-prestamo", tags=["Solicitudes de prestamo"])


@router.post(
    "",
    response_model=SolicitudRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar el prestamo de una obra (Usuario autenticado)",
    description="Crea una solicitud PENDIENTE. Requiere sesion iniciada.",
    responses={
        400: {"description": "La obra no esta disponible"},
        401: {"description": "No autenticado"},
        404: {"description": "La obra o la exposicion no existen"},
        422: {"description": "Datos invalidos"},
    },
)
def crear_solicitud(
    datos: SolicitudCrear,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
    _usuario: Usuario = Depends(obtener_usuario_actual),
):
    return servicio.crear(SolicitudPrestamo(**datos.model_dump()))


@router.get(
    "",
    response_model=list[SolicitudRespuesta],
    summary="Listar solicitudes de prestamo (Usuario autenticado)",
    description="Devuelve todas las solicitudes registradas.",
    responses={401: {"description": "No autenticado"}},
)
def listar_solicitudes(
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
    _usuario: Usuario = Depends(obtener_usuario_actual),
):
    return servicio.listar()


@router.get(
    "/{solicitud_id}",
    response_model=SolicitudRespuesta,
    summary="Obtener una solicitud por ID (Usuario autenticado)",
    description="Devuelve los datos de una solicitud.",
    responses={
        401: {"description": "No autenticado"},
        404: {"description": "La solicitud no existe"},
    },
)
def obtener_solicitud(
    solicitud_id: int,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
    _usuario: Usuario = Depends(obtener_usuario_actual),
):
    return servicio.obtener(solicitud_id)


@router.patch(
    "/{solicitud_id}/aprobar",
    response_model=SolicitudRespuesta,
    summary="Aprobar una solicitud (Solo Admin)",
    description="Aprueba una solicitud pendiente y marca la obra como prestada.",
    responses={
        400: {"description": "Obra no disponible, exposicion sin cupo o solicitud ya resuelta"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes"},
        404: {"description": "La solicitud no existe"},
    },
)
def aprobar_solicitud(
    solicitud_id: int,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
    _admin: Usuario = Depends(exigir_admin),
):
    return servicio.aprobar(solicitud_id)


@router.patch(
    "/{solicitud_id}/rechazar",
    response_model=SolicitudRespuesta,
    summary="Rechazar una solicitud (Solo Admin)",
    description="Rechaza una solicitud pendiente.",
    responses={
        400: {"description": "La solicitud ya fue resuelta"},
        401: {"description": "No autenticado"},
        403: {"description": "Permisos insuficientes"},
        404: {"description": "La solicitud no existe"},
    },
)
def rechazar_solicitud(
    solicitud_id: int,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
    _admin: Usuario = Depends(exigir_admin),
):
    return servicio.rechazar(solicitud_id)
