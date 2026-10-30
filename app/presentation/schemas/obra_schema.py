from datetime import date

from pydantic import BaseModel, ConfigDict, Field

ANIO_ACTUAL = date.today().year


class ObraCrear(BaseModel):
    titulo: str = Field(min_length=2, max_length=150)
    precio_estimado: float = Field(gt=0)
    anio_creacion: int = Field(ge=1000, le=ANIO_ACTUAL)
    estilo: str = Field(min_length=2, max_length=60)
    artista_id: int = Field(gt=0)
    disponible: bool = True


class ObraActualizar(BaseModel):
    titulo: str | None = Field(default=None, min_length=2, max_length=150)
    precio_estimado: float | None = Field(default=None, gt=0)
    anio_creacion: int | None = Field(default=None, ge=1000, le=ANIO_ACTUAL)
    estilo: str | None = Field(default=None, min_length=2, max_length=60)
    disponible: bool | None = None


class ObraRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    precio_estimado: float
    anio_creacion: int
    estilo: str
    disponible: bool
    artista_id: int