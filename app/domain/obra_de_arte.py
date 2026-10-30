from dataclasses import dataclass


@dataclass
class ObraDeArte:
    titulo: str
    precio_estimado: float
    anio_creacion: int
    estilo: str
    artista_id: int
    disponible: bool = True
    id: int | None = None

    def puede_prestarse(self) -> bool:
        return self.disponible

    def marcar_como_prestada(self) -> None:
        self.disponible = False

    def marcar_como_disponible(self) -> None:
        self.disponible = True