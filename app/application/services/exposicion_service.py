from app.domain.excepciones import RecursoNoEncontrado
from app.domain.exposicion import Exposicion
from app.infrastructure.repositories.exposicion_repository import ExposicionRepository


class ExposicionService:
    def __init__(self, repositorio: ExposicionRepository) -> None:
        self.repositorio = repositorio

    def crear(self, exposicion: Exposicion) -> Exposicion:
        return self.repositorio.crear(exposicion)

    def obtener(self, exposicion_id: int) -> Exposicion:
        exposicion = self.repositorio.obtener_por_id(exposicion_id)
        if exposicion is None:
            raise RecursoNoEncontrado("No existe una exposición con el ID solicitado")
        return exposicion

    def listar(self) -> list[Exposicion]:
        return self.repositorio.listar()