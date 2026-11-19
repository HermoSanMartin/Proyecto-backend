import smtplib
from email.message import EmailMessage

from app.infrastructure.config import configuracion


class ServicioCorreoSMTP:
    def enviar_recuperacion(self, destinatario: str, enlace: str) -> None:
        mensaje = EmailMessage()
        mensaje["Subject"] = "Recuperacion de contrasena - Galeria de Arte"
        mensaje["From"] = configuracion.smtp_from
        mensaje["To"] = destinatario
        mensaje.set_content(
            "Se solicito restablecer tu contrasena.\n\n"
            f"Usa el siguiente enlace de un solo uso (valido por {configuracion.recovery_token_expire_minutes} minutos):\n"
            f"{enlace}\n\n"
            "Si no realizaste esta solicitud, ignora este mensaje."
        )
        with smtplib.SMTP(
            configuracion.smtp_host, configuracion.smtp_port, timeout=5
        ) as smtp:
            smtp.send_message(mensaje)
