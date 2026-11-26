from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status

from app.application.services.obra_service import ObraService
from app.domain.obra_de_arte import ObraDeArte
from app.domain.usuario import Usuario
from app.presentation.dependencies import exigir_admin, obtener_servicio_obra
from app.presentation.schemas.obra_schema import (
    ObraActualizar,
    ObraCrear,
    ObraRespuesta,
    PaginaObras,
)
from app.presentation.schemas.respuesta import RespuestaError

router = APIRouter(prefix="/api/v1/obras", tags=["Obras de arte"])


@router.post(
    "",
    response_model=ObraRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una obra de arte (Solo Admin)",
    description="Crea una obra asociada a un artista existente. Requiere rol administrador.",
    responses={
        401: {"model": RespuestaError, "description": "No autenticado"},
        403: {"model": RespuestaError, "description": "Permisos insuficientes"},
        404: {"model": RespuestaError, "description": "El artista no existe"},
        422: {"model": RespuestaError, "description": "Datos invalidos"},
    },
)
def crear_obra(
    datos: ObraCrear,
    servicio: ObraService = Depends(obtener_servicio_obra),
    _admin: Usuario = Depends(exigir_admin),
):
    return servicio.crear(ObraDeArte(**datos.model_dump()))


@router.get(
    "",
    response_model=PaginaObras,
    summary="Listar obras con filtro, orden y paginacion",
    description="Primero filtra por estilo, luego ordena y finalmente pagina.",
)
def listar_obras(
    estilo: str | None = Query(default=None, description="Filtra por estilo exacto"),
    ordenar_por: Literal["titulo", "precio_estimado", "anio_creacion", "estilo"] = "titulo",
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=10, ge=1, le=100),
    servicio: ObraService = Depends(obtener_servicio_obra),
):
    obras, total, total_paginas = servicio.listar(estilo, ordenar_por, direccion, pagina, limite)
    return PaginaObras(
        items=[ObraRespuesta.model_validate(o) for o in obras],
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=total_paginas,
    )


@router.get(
    "/{obra_id}",
    response_model=ObraRespuesta,
    summary="Obtener una obra por ID",
    description="Devuelve los datos de una obra.",
    responses={404: {"model": RespuestaError, "description": "La obra no existe"}},
)
def obtener_obra(obra_id: int, servicio: ObraService = Depends(obtener_servicio_obra)):
    return servicio.obtener(obra_id)


@router.patch(
    "/{obra_id}",
    response_model=ObraRespuesta,
    summary="Actualizar una obra (Solo Admin)",
    description="Modifica solo los campos enviados. Requiere rol administrador.",
    responses={
        401: {"model": RespuestaError, "description": "No autenticado"},
        403: {"model": RespuestaError, "description": "Permisos insuficientes"},
        404: {"model": RespuestaError, "description": "La obra no existe"},
    },
)
def actualizar_obra(
    obra_id: int,
    datos: ObraActualizar,
    servicio: ObraService = Depends(obtener_servicio_obra),
    _admin: Usuario = Depends(exigir_admin),
):
    return servicio.actualizar(obra_id, datos.model_dump(exclude_unset=True))


@router.delete(
    "/{obra_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una obra (Solo Admin)",
    description="Elimina la obra de forma permanente. Requiere rol administrador.",
    responses={
        401: {"model": RespuestaError, "description": "No autenticado"},
        403: {"model": RespuestaError, "description": "Permisos insuficientes"},
        404: {"model": RespuestaError, "description": "La obra no existe"},
    },
)
def eliminar_obra(
    obra_id: int,
    servicio: ObraService = Depends(obtener_servicio_obra),
    _admin: Usuario = Depends(exigir_admin),
):
    servicio.eliminar(obra_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
