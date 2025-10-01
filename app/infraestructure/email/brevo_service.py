from app.infraestructure.email.interface import EmailService
import requests
from app.settings import settings

class BrevoEmailService(EmailService):
    def __init__(self, api_key: str = settings.brevo_api_key):
        self.api_key = api_key

    def send_email(self, to: str, subject: str, html_content: str):
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": self.api_key, "Content-Type": "application/json"},
            json={
                "sender": {"name": "Spotly", "email": "no-reply@spotly.work"},
                "to": [{"email": to}],
                "subject": subject,
                "htmlContent": html_content
            }
        )
        response.raise_for_status()