import resend
from app.infrastructure.email.interface import IEmailService


class ResendEmailService(IEmailService):
    def __init__(self, api_key: str, sender: str):
        resend.api_key = api_key
        self.sender = sender

    def send_email(self, to: str, subject: str, body: str) -> None:
        try:
            payload = {
                "from": self.sender,
                "to": [to],
                "subject": subject,
                "html": body,
            }

            resend.Emails.send(**payload)

        except Exception as e:
            raise RuntimeError(f"Fallo al enviar email: {e}")
