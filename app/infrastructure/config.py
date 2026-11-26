from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    database_url: str
    demo_admin_password: SecretStr | None = None
    demo_visitante_password: SecretStr | None = None

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    recovery_token_expire_minutes: int = 15
    cookie_secure: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_from: str = "no-responder@galeria-uct.cl"
    url_recuperacion_base: str = "http://localhost:8000/api/v1/auth/restablecer-password"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def lista_cors_origins(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origins.split(",") if origen.strip()]


configuracion = Configuracion()
