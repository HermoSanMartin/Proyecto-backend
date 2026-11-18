from app.domain.excepciones import RecursoNoEncontrado
from app.domain.obra_de_arte import ObraDeArte
from app.infrastructure.repositories.artista_repository import ArtistaRepository
from app.infrastructure.repositories.obra_repository import ObraRepository


class ObraService:
    def __init__(self, repo_obras: ObraRepository, repo_artistas: ArtistaRepository) -> None:
        self.repo_obras = repo_obras
        self.repo_artistas = repo_artistas

    def crear(self, obra: ObraDeArte) -> ObraDeArte:
        if self.repo_artistas.obtener_por_id(obra.artista_id) is None:
            raise RecursoNoEncontrado("No existe un artista con el ID indicado")
        return self.repo_obras.crear(obra)

    def obtener(self, obra_id: int) -> ObraDeArte:
        obra = self.repo_obras.obtener_por_id(obra_id)
        if obra is None:
            raise RecursoNoEncontrado("No existe una obra con el ID solicitado")
        return obra

    def listar(self, estilo, ordenar_por, direccion, pagina, limite):
        return self.repo_obras.listar(estilo, ordenar_por, direccion, pagina, limite)

    def actualizar(self, obra_id: int, cambios: dict) -> ObraDeArte:
        obra = self.obtener(obra_id)
        for campo, valor in cambios.items():
            setattr(obra, campo, valor)
        return self.repo_obras.actualizar(obra)

    def eliminar(self, obra_id: int) -> None:
        if not self.repo_obras.eliminar(obra_id):
            raise RecursoNoEncontrado("No existe una obra con el ID solicitado")