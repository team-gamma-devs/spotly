import csv
from typing import List
import logging

from app.domain.invitation import Invitation
from app.services.csv_invitation.exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)
from app.infrastructure.email import resend_email_service
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)

logger = logging.getLogger(__name__)


class CSVInvitationProcessor:
    """
    Handles the processing of CSV files containing graduate information.

    Responsibilities:
    1. Validates the CSV file for required columns and correct formatting.
    2. Generates Invitation objects for each graduate.
    3. Persists the invitations to the database via InvitationRepository.
    4. Sends invitation emails using the configured email service.

    Attributes:
        REQUIRED_COLUMNS (List[str]): Columns required in the CSV file.
        email_service: Service responsible for sending emails.
        invitation_repo (InvitationRepository): Repository for saving invitations. Can be mocked for testing.
    """

    REQUIRED_COLUMNS = ["first_name", "last_name", "cohort", "email"]

    def __init__(self, email_service=resend_email_service, invitation_repo=None):
        """
        Initializes the CSVInvitationProcessor with optional email service and invitation repository.

        Args:
            email_service: Optional; service used to send emails. Defaults to resend_email_service.
            invitation_repo: Optional; instance of InvitationRepository or mock for testing.
        """
        self.email_service = email_service
        # invitation_repo parameter allows mocking the repository during testing.
        self.invitation_repo = invitation_repo or InvitationRepository()

    def process_csv(self, file_contents: bytes) -> List[Invitation]:
        """
        Orchestrates the complete CSV processing flow.

        Steps:
        1. Validate CSV contents.
        2. Generate Invitation objects.
        3. Save invitations to the database.

        Args:
            file_contents (bytes): Raw CSV file contents.

        Returns:
            List[Invitation]: List of Invitation objects created from CSV.
        """
        graduates = self._validate_csv(file_contents)
        invitations = self._generate_invitations(graduates)
        self._save_invitations(invitations)
        return invitations

    def _validate_csv(self, file_contents: bytes) -> List[dict]:
        """
        Validates CSV contents for correct formatting and required columns.

        Args:
            file_contents (bytes): Raw CSV file contents.

        Returns:
            List[dict]: List of dictionaries representing each row in the CSV.

        Raises:
            InvalidCSVException: If CSV is empty, malformed, or cannot be decoded.
            MissingColumnsException: If required columns are missing.
        """
        try:
            content = file_contents.decode("utf-8")
            reader = csv.DictReader(content.splitlines())
        except UnicodeDecodeError:
            raise InvalidCSVException("Not valid CSV")

        if not reader.fieldnames:
            raise InvalidCSVException("CSV is empty or missing header")

        missing = [col for col in self.REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise MissingColumnsException(missing)

        return list(reader)

    def _generate_invitations(self, graduates: list) -> List[Invitation]:
        """
        Generates Invitation objects from validated graduate data.

        Args:
            graduates (list): List of dictionaries representing graduates.

        Returns:
            List[Invitation]: List of Invitation objects.
        """
        invitations = []
        for graduated in graduates:
            invitation = Invitation(
                full_name=f"{graduated['first_name']} {graduated['last_name']}",
                cohort=int(graduated["cohort"]),
                email=graduated["email"],
            )
            invitations.append(invitation)
        return invitations

    def _save_invitations(self, invitations: List[Invitation]):
        """
        Saves Invitation objects to the database using the repository.
        Logs success or failure for each invitation.

        Args:
            invitations (List[Invitation]): List of Invitation objects to save.
        """
        for invitation in invitations:
            try:
                self.invitation_repo.create(invitation.to_dict())
                logger.info(f"Invitation saved successfully for {invitation.email}")
            except Exception as e:
                logger.error(
                    f"Failed to save invitation for {invitation.email}: {str(e)}",
                    exc_info=True,
                )

    def send_invitations(self, invitations: List[Invitation]):
        """
        Sends invitation emails for the provided Invitation objects.
        Logs success or failure for each email.

        Args:
            invitations (List[Invitation]): List of Invitation objects to email.
        """
        for invitation in invitations:
            try:
                body = self._build_email_body(invitation)
                self.email_service.send_email(
                    invitation.email,
                    "Spotly app invitation from Holberton",
                    body,
                )
                logger.info(f"Invitation email sent successfully to {invitation.email}")
            except Exception as e:
                logger.error(
                    f"Failed to send email to {invitation.email}: {str(e)}",
                    exc_info=True,
                )

    def _build_email_body(self, invitation: Invitation) -> str:
        """
        Builds the HTML body for the invitation email.

        Args:
            invitation (Invitation): The Invitation object for which to build the email.

        Returns:
            str: HTML string representing the email body.
        """
        return f"""
        <div style="
            width: 100%;
            min-height: 300px;
            max-width: 1200px;
            margin: 0 auto;
            background-color: #ffffff;
            font-family: Arial, sans-serif;
        ">
            <section id="header" style="
                    background: linear-gradient(to right, #cb5554, #e9a075);
                    padding: 20px;
                    color: rgb(234, 245, 255);
                    font-family: Arial, sans-serif;
                ">
            <h1 style="margin: 0; margin-left: 20px;">Welcome to Spotly!</h1>
            </section>

            <section id="body" style="
                padding: 20px;
                font-family: Arial, sans-serif;
            ">
                <h2>Hello! {invitation.full_name}</h2>
                <h4>To log in and start using Spotly please use this link: <span style="color: red">http://spotly.work/sign-up/invite?token={invitation.token}</span></h4>
            </section>
            
            <section id="footer" style="
                background: linear-gradient(to right, #cb5554, #e9a075);
                padding: 20px;
                color: rgb(234, 245, 255);
                font-family: Arial, sans-serif;
                text-align: center;
                font-size: 0.9em;
                margin-top: 20px;
            ">
                <p style="margin: 0.5em 0;">Thanks for using Spotly!</p>
                <p style="margin: 0.5em 0; font-size: 0.8em;">
                    If you have any questions, contact a
                    <a href="https://spotly.work/contact" style="color: rgb(234, 245, 255); text-decoration: underline;">Spotly Supervisor</a>
                    agent
                </p>
                <p style="margin: 0.5em 0; font-size: 0.7em; opacity: 0.8;">
                    2025 Spotly. Pending Rights Reservation.
                </p>
            </section>
        </div>
        """
