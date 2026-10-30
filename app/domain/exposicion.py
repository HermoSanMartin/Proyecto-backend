from dataclasses import dataclass
from datetime import date
from enum import Enum

MAX_OBRAS_PRESTADAS = 5


class EstadoExposicion(str, Enum):
    PLANIFICADA = "PLANIFICADA"
    EN_CURSO = "EN_CURSO"
    FINALIZADA = "FINALIZADA"


@dataclass
class Exposicion:
    nombre_evento: str
    lugar: str
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoExposicion = EstadoExposicion.PLANIFICADA
    id: int | None = None

    def __post_init__(self) -> None:
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La exposición no puede terminar antes de comenzar")

    def tiene_cupo(self, obras_prestadas: int) -> bool:
        return obras_prestadas < MAX_OBRAS_PRESTADAS