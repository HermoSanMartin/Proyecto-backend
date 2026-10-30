from dataclasses import dataclass


@dataclass
class Artista:
    nombre_artistico: str
    email: str
    nacionalidad: str
    biografia: str
    activo: bool = True
    id: int | None = None

    def desactivar(self) -> None:
        self.activo = False