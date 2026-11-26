from datetime import date

from pydantic import BaseModel, Field, model_validator

from app.domain.exposicion import EstadoExposicion
from app.presentation.schemas.respuesta import ApiResponse


class ExposicionCrear(BaseModel):
    nombre_evento: str = Field(min_length=3, max_length=150)
    lugar: str = Field(min_length=2, max_length=150)
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoExposicion = EstadoExposicion.PLANIFICADA

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La exposición no puede terminar antes de comenzar")
        return self


class ExposicionRespuesta(ApiResponse):
    id: int
    nombre_evento: str
    lugar: str
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoExposicion
