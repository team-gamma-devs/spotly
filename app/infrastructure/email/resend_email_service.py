import resend

from app.domain.ports.email_service_port import IEmailService


class ResendEmailService(IEmailService):
    def __init__(
        self,
        api_key: str,
        sender: str,
        daily_limit: int = 100,
        per_second_limit: int = 2,
    ):
        resend.api_key = api_key
        self.sender = sender
        self.daily_limit = daily_limit
        self.per_second_limit = per_second_limit

    def send_email(self, to: str, subject: str, body: str) -> None:
        """
        Intenta enviar un correo. Si Resend responde con error, lanza excepción
        que puede ser capturada por el worker para retry o logging.
        """
        try:
            resend.Emails.send(
                {"from": self.sender, "to": [to], "subject": subject, "html": body}
            )
        except resend.ResendError as e:
            # Resend generic error.
            raise Exception(f"ResendError: {e}")
        except resend.RateLimitError as e:
            # Lmit exceeded (Daily or per second)
            raise Exception(f"RateLimitExceeded: {e}")
        except Exception as e:
            # Other errors
            raise Exception(f"UnexpectedError: {e}")
