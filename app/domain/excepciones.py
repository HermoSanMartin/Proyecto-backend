class ErrorDeDominio(Exception):
    codigo = "DOMAIN_ERROR"

    def __init__(self, mensaje: str, detalles: list | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalles = detalles or []


class RecursoNoEncontrado(ErrorDeDominio):
    codigo = "RESOURCE_NOT_FOUND"


class ReglaDeNegocioViolada(ErrorDeDominio):
    codigo = "BUSINESS_RULE_VIOLATION"


class ConflictoDeEstado(ErrorDeDominio):
    codigo = "CONFLICT"