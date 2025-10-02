import resend
from typing import Protocol


class IEmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> None:
        ...


class ResendEmailService(IEmailService):
    def __init__(self, api_key: str, sender: str):
        resend.api_key = api_key
        self.sender = sender

    def send_email(self, to: str, subject: str, body: str) -> None:
        try:
            resend.Emails.send({
                "from": self.sender,
                "to": [to],
                "subject": subject,
                "html": body
            })
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")