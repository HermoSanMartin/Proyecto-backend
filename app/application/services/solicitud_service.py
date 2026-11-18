from app.domain.excepciones import RecursoNoEncontrado, ReglaDeNegocioViolada
from app.domain.solicitud_prestamo import SolicitudPrestamo
from app.infrastructure.repositories.exposicion_repository import ExposicionRepository
from app.infrastructure.repositories.obra_repository import ObraRepository
from app.infrastructure.repositories.solicitud_repository import SolicitudRepository


class SolicitudService:
    def __init__(
        self,
        repo_solicitudes: SolicitudRepository,
        repo_obras: ObraRepository,
        repo_exposiciones: ExposicionRepository,
    ) -> None:
        self.repo_solicitudes = repo_solicitudes
        self.repo_obras = repo_obras
        self.repo_exposiciones = repo_exposiciones

    def crear(self, solicitud: SolicitudPrestamo) -> SolicitudPrestamo:
        obra = self.repo_obras.obtener_por_id(solicitud.obra_id)
        if obra is None:
            raise RecursoNoEncontrado("No existe una obra con el ID indicado")
        if self.repo_exposiciones.obtener_por_id(solicitud.exposicion_id) is None:
            raise RecursoNoEncontrado("No existe una exposición con el ID indicado")
        # Regla 1: solo se puede solicitar una obra disponible
        if not obra.puede_prestarse():
            raise ReglaDeNegocioViolada("La obra no está disponible para préstamo")
        return self.repo_solicitudes.crear(solicitud)

    def obtener(self, solicitud_id: int) -> SolicitudPrestamo:
        solicitud = self.repo_solicitudes.obtener_por_id(solicitud_id)
        if solicitud is None:
            raise RecursoNoEncontrado("No existe una solicitud con el ID solicitado")
        return solicitud

    def listar(self) -> list[SolicitudPrestamo]:
        return self.repo_solicitudes.listar()

    def aprobar(self, solicitud_id: int) -> SolicitudPrestamo:
        solicitud = self.obtener(solicitud_id)
        solicitud.aprobar()  # falla si la solicitud no está pendiente

        obra = self.repo_obras.obtener_por_id(solicitud.obra_id)
        exposicion = self.repo_exposiciones.obtener_por_id(solicitud.exposicion_id)

        # Regla 1: la obra pudo haberse prestado a otra exposición mientras tanto
        if not obra.puede_prestarse():
            raise ReglaDeNegocioViolada("La obra no está disponible para préstamo")

        # Regla 2: máximo 5 obras prestadas por exposición
        prestadas = self.repo_solicitudes.contar_aprobadas(solicitud.exposicion_id)
        if not exposicion.tiene_cupo(prestadas):
            raise ReglaDeNegocioViolada(
                "La exposición ya alcanzó el máximo de 5 obras prestadas"
            )

        obra.marcar_como_prestada()
        self.repo_obras.actualizar(obra)
        return self.repo_solicitudes.actualizar(solicitud)

    def rechazar(self, solicitud_id: int) -> SolicitudPrestamo:
        solicitud = self.obtener(solicitud_id)
        solicitud.rechazar()
        return self.repo_solicitudes.actualizar(solicitud)