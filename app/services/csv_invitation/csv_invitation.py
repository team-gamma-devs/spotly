import csv
from typing import BinaryIO, List

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

    def process_csv(self, file: BinaryIO):
        """Orquesta todo el flujo de validación, creación, guardado y envío"""
        graduates = self._validate_csv(file)
        invitations = self._generate_invitations(graduates)
        self._send_invitations(invitations)

    # Private methods (Modularization).
    def _validate_csv(self, file: BinaryIO):
        try:
            file.seek(0)
            reader = csv.DictReader(file.read().decode("utf-8").splitlines())
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

    def _send_invitations(self, invitations: List[Invitation]):
        for invitation in invitations:
            self.email_service.send_email(
                invitation.email,
                "Spotly app invitation from Holberton",
                f"<strong>Hola! {invitation.full_name}</strong>\
                    <br>\
                    <br>\
                    <p>Esta es una invitación de prueba</p>",
            )
