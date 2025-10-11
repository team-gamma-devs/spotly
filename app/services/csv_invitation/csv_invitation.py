import csv
from typing import List

from app.domain.invitation import Invitation
from app.services.csv_invitation.exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)
from app.infrastructure.email import resend_email_service


class CSVInvitationProcessor:
    REQUIRED_COLUMNS = ["first_name", "last_name", "cohort", "email"]

    def __init__(self, email_service=resend_email_service):
        self.email_service = email_service

    def process_csv(self, file_contents: bytes):
        """Orquesta todo el flujo de validación, creación, guardado y envío"""
        graduates = self._validate_csv(file_contents)
        invitations = self._generate_invitations(graduates)
        return invitations

    # Private methods (Modularization).
    def _validate_csv(self, file_contents: bytes):
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

    def _generate_invitations(self, graduates: list):
        invitations = []
        for graduated in graduates:
            invitation = Invitation(
                full_name=f"{graduated['first_name']} {graduated['last_name']}",
                cohort=int(graduated["cohort"]),
                email=graduated["email"],
            )
            invitations.append(invitation)
        return invitations

    def send_invitations(self, invitations: List[Invitation]):
        for invitation in invitations:
            body = self._build_email_body(invitation)
            self.email_service.send_email(
                invitation.email,
                "Spotly app invitation from Holberton",
                body,
            )

    def _build_email_body(self, invitation: Invitation) -> str:
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
