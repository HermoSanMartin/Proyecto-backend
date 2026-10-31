from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from app.domain.excepciones import ReglaDeNegocioViolada


class EstadoSolicitud(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


@dataclass
class SolicitudPrestamo:
    obra_id: int
    exposicion_id: int
    dias_prestamo: int
    fecha_solicitud: date = field(default_factory=date.today)
    estado_solicitud: EstadoSolicitud = EstadoSolicitud.PENDIENTE
    id: int | None = None

    def __post_init__(self) -> None:
        if self.dias_prestamo < 1:
            raise ReglaDeNegocioViolada("El préstamo debe durar al menos 1 día")

    @property
    def fecha_fin_prestamo(self) -> date:
        return self.fecha_solicitud + timedelta(days=self.dias_prestamo)

    def aprobar(self) -> None:
        self._cambiar_estado(EstadoSolicitud.APROBADO)

    def rechazar(self) -> None:
        self._cambiar_estado(EstadoSolicitud.RECHAZADO)

    def _cambiar_estado(self, nuevo_estado: EstadoSolicitud) -> None:
        if self.estado_solicitud != EstadoSolicitud.PENDIENTE:
            raise ReglaDeNegocioViolada("Solo se puede resolver una solicitud pendiente")
        self.estado_solicitud = nuevo_estado
