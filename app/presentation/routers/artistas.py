from fastapi import APIRouter, Depends, status

from app.application.services.artista_service import ArtistaService
from app.domain.artista import Artista
from app.domain.usuario import Usuario
from app.presentation.dependencies import exigir_admin, obtener_servicio_artista
from app.presentation.schemas.artista_schema import (
    ArtistaActualizar,
    ArtistaCrear,
    ArtistaRespuesta,
)
from app.presentation.schemas.respuesta import RespuestaError

router = APIRouter(prefix="/api/v1/artistas", tags=["Artistas"])


@router.post(
    "",
    response_model=ArtistaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un artista (Solo Admin)",
    description="Crea un artista nuevo. Requiere rol administrador.",
    responses={
        401: {"model": RespuestaError, "description": "No autenticado"},
        403: {"model": RespuestaError, "description": "Permisos insuficientes"},
        409: {"model": RespuestaError, "description": "Ya existe un artista con ese correo"},
        422: {"model": RespuestaError, "description": "Datos invalidos"},
    },
)
def crear_artista(
    datos: ArtistaCrear,
    servicio: ArtistaService = Depends(obtener_servicio_artista),
    _admin: Usuario = Depends(exigir_admin),
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
    responses={404: {"model": RespuestaError, "description": "El artista no existe"}},
)
def obtener_artista(
    artista_id: int,
    servicio: ArtistaService = Depends(obtener_servicio_artista),
):
    return servicio.obtener(artista_id)


@router.patch(
    "/{artista_id}",
    response_model=ArtistaRespuesta,
    summary="Actualizar un artista (Solo Admin)",
    description="Modifica solo los campos enviados. Requiere rol administrador.",
    responses={
        401: {"model": RespuestaError, "description": "No autenticado"},
        403: {"model": RespuestaError, "description": "Permisos insuficientes"},
        404: {"model": RespuestaError, "description": "El artista no existe"},
        409: {"model": RespuestaError, "description": "Correo ya usado por otro artista"},
    },
)
def actualizar_artista(
    artista_id: int,
    datos: ArtistaActualizar,
    servicio: ArtistaService = Depends(obtener_servicio_artista),
    _admin: Usuario = Depends(exigir_admin),
):
    return servicio.actualizar(artista_id, datos.model_dump(exclude_unset=True))
