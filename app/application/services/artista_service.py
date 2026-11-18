from app.domain.artista import Artista
from app.domain.excepciones import ConflictoDeEstado, RecursoNoEncontrado
from app.infrastructure.repositories.artista_repository import ArtistaRepository


class ArtistaService:
    def __init__(self, repositorio: ArtistaRepository) -> None:
        self.repositorio = repositorio

    def crear(self, artista: Artista) -> Artista:
        if self.repositorio.obtener_por_email(artista.email):
            raise ConflictoDeEstado("Ya existe un artista con ese correo electrónico")
        return self.repositorio.crear(artista)

    def obtener(self, artista_id: int) -> Artista:
        artista = self.repositorio.obtener_por_id(artista_id)
        if artista is None:
            raise RecursoNoEncontrado("No existe un artista con el ID solicitado")
        return artista

    def listar(self) -> list[Artista]:
        return self.repositorio.listar()

    def actualizar(self, artista_id: int, cambios: dict) -> Artista:
        artista = self.obtener(artista_id)
        nuevo_email = cambios.get("email")
        if nuevo_email and nuevo_email != artista.email:
            if self.repositorio.obtener_por_email(nuevo_email):
                raise ConflictoDeEstado("Ya existe un artista con ese correo electrónico")
        for campo, valor in cambios.items():
            setattr(artista, campo, valor)
        return self.repositorio.actualizar(artista)