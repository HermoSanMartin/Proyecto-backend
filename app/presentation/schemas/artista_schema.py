from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ArtistaCrear(BaseModel):
    nombre_artistico: str = Field(min_length=2, max_length=100)
    email: EmailStr
    nacionalidad: str = Field(min_length=2, max_length=60)
    biografia: str = Field(default="", max_length=1000)


class ArtistaActualizar(BaseModel):
    nombre_artistico: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    nacionalidad: str | None = Field(default=None, min_length=2, max_length=60)
    biografia: str | None = Field(default=None, max_length=1000)
    activo: bool | None = None


class ArtistaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_artistico: str
    email: EmailStr
    nacionalidad: str
    biografia: str
    activo: bool