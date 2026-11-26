from datetime import date

from pydantic import BaseModel, Field

from app.domain.solicitud_prestamo import EstadoSolicitud
from app.presentation.schemas.respuesta import ApiResponse


class SolicitudCrear(BaseModel):
    obra_id: int = Field(gt=0)
    exposicion_id: int = Field(gt=0)
    dias_prestamo: int = Field(ge=1, le=365)


class SolicitudRespuesta(ApiResponse):
    id: int
    obra_id: int
    exposicion_id: int
    dias_prestamo: int
    fecha_solicitud: date
    fecha_fin_prestamo: date
    estado_solicitud: EstadoSolicitud
