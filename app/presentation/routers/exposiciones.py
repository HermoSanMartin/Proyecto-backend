from fastapi import APIRouter, Depends, status

from app.application.services.exposicion_service import ExposicionService
from app.domain.exposicion import Exposicion
from app.presentation.dependencies import obtener_servicio_exposicion
from app.presentation.schemas.exposicion_schema import ExposicionCrear, ExposicionRespuesta

router = APIRouter(prefix="/api/v1/exposiciones", tags=["Exposiciones"])


@router.post(
    "",
    response_model=ExposicionRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una exposición",
    description="Crea una exposición. La fecha de término no puede ser anterior a la de inicio.",
    responses={422: {"description": "Datos inválidos o fechas incoherentes"}},
)
def crear_exposicion(
    datos: ExposicionCrear,
    servicio: ExposicionService = Depends(obtener_servicio_exposicion),
):
    return servicio.crear(Exposicion(**datos.model_dump()))


@router.get(
    "",
    response_model=list[ExposicionRespuesta],
    summary="Listar exposiciones",
    description="Devuelve todas las exposiciones registradas.",
)
def listar_exposiciones(servicio: ExposicionService = Depends(obtener_servicio_exposicion)):
    return servicio.listar()


@router.get(
    "/{exposicion_id}",
    response_model=ExposicionRespuesta,
    summary="Obtener una exposición por ID",
    description="Devuelve los datos de una exposición.",
    responses={404: {"description": "La exposición no existe"}},
)
def obtener_exposicion(
    exposicion_id: int,
    servicio: ExposicionService = Depends(obtener_servicio_exposicion),
):
    return servicio.obtener(exposicion_id)