import resend
from app.domain.ports.email_service_port import IEmailService


class ResendEmailService(IEmailService):
    """
    Email service implementation using the Resend API.

    Attributes:
        sender (str): Email address used as the sender.
        daily_limit (int): Maximum emails allowed per day.
        per_second_limit (int): Maximum emails allowed per second.
    """

    def __init__(
        self,
        api_key: str,
        sender: str,
        daily_limit: int = 100,
        per_second_limit: int = 2,
    ):
        """
        Initialize the Resend email service with API key, sender, and optional limits.

        Args:
            api_key (str): API key for the Resend service.
            sender (str): Sender email address.
            daily_limit (int, optional): Daily sending limit. Defaults to 100.
            per_second_limit (int, optional): Per-second sending limit. Defaults to 2.
        """
        resend.api_key = api_key
        self.sender = sender
        self.daily_limit = daily_limit
        self.per_second_limit = per_second_limit

    def send_email(self, to: str, subject: str, body: str) -> None:
        """
        Send an email using Resend.

        Args:
            to (str): Recipient email address.
            subject (str): Subject of the email.
            body (str): HTML content of the email.

        Raises:
            Exception: Raises a generic exception wrapping Resend errors:
                - ResendError: If Resend API responds with a generic error.
                - RateLimitExceeded: If sending exceeds daily or per-second limits.
                - UnexpectedError: Any other unexpected errors during sending.
        """
        try:
            resend.Emails.send(
                {"from": self.sender, "to": [to], "subject": subject, "html": body}
            )
        except resend.ResendError as e:
            raise Exception(f"ResendError: {e}")
        except resend.RateLimitError as e:
            raise Exception(f"RateLimitExceeded: {e}")
        except Exception as e:
            raise Exception(f"UnexpectedError: {e}")
