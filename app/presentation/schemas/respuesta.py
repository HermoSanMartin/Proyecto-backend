from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    """Configuracion compartida por los DTO de salida de la API."""

    model_config = ConfigDict(from_attributes=True)


class ErrorAPI(BaseModel):
    code: str
    message: str
    details: list = Field(default_factory=list)


class RespuestaError(ApiResponse):
    error: ErrorAPI
