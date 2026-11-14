from fastapi import APIRouter, Depends, status

from app.application.services.solicitud_service import SolicitudService
from app.domain.solicitud_prestamo import SolicitudPrestamo
from app.presentation.dependencies import obtener_servicio_solicitud
from app.presentation.schemas.solicitud_schema import SolicitudCrear, SolicitudRespuesta

router = APIRouter(prefix="/api/v1/solicitudes-prestamo", tags=["Solicitudes de préstamo"])


@router.post(
    "",
    response_model=SolicitudRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar el préstamo de una obra",
    description="Crea una solicitud PENDIENTE. La obra debe existir y estar disponible.",
    responses={400: {"description": "La obra no está disponible"},
               404: {"description": "La obra o la exposición no existen"},
               422: {"description": "Datos inválidos"}},
)
def crear_solicitud(
    datos: SolicitudCrear,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
):
    return servicio.crear(SolicitudPrestamo(**datos.model_dump()))


@router.get(
    "",
    response_model=list[SolicitudRespuesta],
    summary="Listar solicitudes de préstamo",
    description="Devuelve todas las solicitudes registradas.",
)
def listar_solicitudes(servicio: SolicitudService = Depends(obtener_servicio_solicitud)):
    return servicio.listar()


@router.get(
    "/{solicitud_id}",
    response_model=SolicitudRespuesta,
    summary="Obtener una solicitud por ID",
    description="Devuelve los datos de una solicitud.",
    responses={404: {"description": "La solicitud no existe"}},
)
def obtener_solicitud(
    solicitud_id: int,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
):
    return servicio.obtener(solicitud_id)


@router.patch(
    "/{solicitud_id}/aprobar",
    response_model=SolicitudRespuesta,
    summary="Aprobar una solicitud",
    description="Aprueba una solicitud pendiente y marca la obra como prestada.",
    responses={400: {"description": "Obra no disponible, exposición sin cupo o solicitud ya resuelta"},
               404: {"description": "La solicitud no existe"}},
)
def aprobar_solicitud(
    solicitud_id: int,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
):
    return servicio.aprobar(solicitud_id)


@router.patch(
    "/{solicitud_id}/rechazar",
    response_model=SolicitudRespuesta,
    summary="Rechazar una solicitud",
    description="Rechaza una solicitud pendiente.",
    responses={400: {"description": "La solicitud ya fue resuelta"},
               404: {"description": "La solicitud no existe"}},
)
def rechazar_solicitud(
    solicitud_id: int,
    servicio: SolicitudService = Depends(obtener_servicio_solicitud),
):
    return servicio.rechazar(solicitud_id)