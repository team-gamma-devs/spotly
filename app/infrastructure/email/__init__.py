from app.infrastructure.email.resend_email_service import ResendEmailService
from app.settings import settings


resend_email_service = ResendEmailService(
    settings.resend_api_key, "onboarding@resend.dev"
)
