from fastapi import APIRouter, Depends, status

from app.application.services.artista_service import ArtistaService
from app.domain.artista import Artista
from app.presentation.dependencies import obtener_servicio_artista
from app.presentation.schemas.artista_schema import (
    ArtistaActualizar,
    ArtistaCrear,
    ArtistaRespuesta,
)

router = APIRouter(prefix="/api/v1/artistas", tags=["Artistas"])


@router.post(
    "",
    response_model=ArtistaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un artista",
    description="Crea un artista nuevo. El correo electrónico debe ser único.",
    responses={409: {"description": "Ya existe un artista con ese correo"},
               422: {"description": "Datos inválidos"}},
)
def crear_artista(
    datos: ArtistaCrear,
    servicio: ArtistaService = Depends(obtener_servicio_artista),
):
    return servicio.crear(Artista(**datos.model_dump()))


@router.get(
    "",
    response_model=list[ArtistaRespuesta],
    summary="Listar artistas",
    description="Devuelve todos los artistas registrados.",
)
def listar_artistas(servicio: ArtistaService = Depends(obtener_servicio_artista)):
    return servicio.listar()


@router.get(
    "/{artista_id}",
    response_model=ArtistaRespuesta,
    summary="Obtener un artista por ID",
    description="Devuelve los datos de un artista.",
    responses={404: {"description": "El artista no existe"}},
)
def obtener_artista(
    artista_id: int,
    servicio: ArtistaService = Depends(obtener_servicio_artista),
):
    return servicio.obtener(artista_id)


@router.patch(
    "/{artista_id}",
    response_model=ArtistaRespuesta,
    summary="Actualizar un artista",
    description="Modifica solo los campos enviados.",
    responses={404: {"description": "El artista no existe"},
               409: {"description": "Correo ya usado por otro artista"}},
)
def actualizar_artista(
    artista_id: int,
    datos: ArtistaActualizar,
    servicio: ArtistaService = Depends(obtener_servicio_artista),
):
    return servicio.actualizar(artista_id, datos.model_dump(exclude_unset=True))