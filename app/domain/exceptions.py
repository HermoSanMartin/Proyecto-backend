class ReglaDeNegocioError(Exception):
    """Base de los errores por reglas de negocio del dominio."""

    code = "REGLA_DE_NEGOCIO"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ObraNoDisponibleError(ReglaDeNegocioError):
    code = "OBRA_NO_DISPONIBLE"


class ExposicionSinCupoError(ReglaDeNegocioError):
    code = "EXPOSICION_SIN_CUPO"


class FechasInvalidasError(ReglaDeNegocioError):
    code = "FECHAS_INVALIDAS"


class SolicitudYaResueltaError(ReglaDeNegocioError):
    code = "SOLICITUD_YA_RESUELTA"