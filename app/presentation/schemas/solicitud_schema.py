from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.domain.solicitud_prestamo import EstadoSolicitud


class SolicitudCrear(BaseModel):
    obra_id: int = Field(gt=0)
    exposicion_id: int = Field(gt=0)
    dias_prestamo: int = Field(ge=1, le=365)


class SolicitudRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    obra_id: int
    exposicion_id: int
    dias_prestamo: int
    fecha_solicitud: date
    fecha_fin_prestamo: date
    estado_solicitud: EstadoSolicitud