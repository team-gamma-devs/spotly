import csv
from typing import TextIO, List

from app.domain.invitation import Invitation
from .exceptions import InvalidCSVException, MissingColumnsException


class CSVInvitationProcessor:
    REQUIRED_COLUMNS = ["first_name", "last_name", "cohort", "email"]

    def __init__(self, invitation_repo, email_service):
        self.invitation_repo = invitation_repo
        self.email_service = email_service

    def process_csv(self, file: TextIO):
        """Orquesta todo el flujo de validación, creación, guardado y envío"""
        graduates = self._validate_csv(file)
        invitations = self._generate_invitations(graduates)
        self._save_invitations(invitations)
        return self._send_invitations(invitations)


    # Private methods (Modularization).
    def _validate_csv(self, file: TextIO):
        try:
            file.seek(0)
            reader = csv.DictReader(file.read().decode("utf-8").splitlines())
        except UnicodeDecodeError:
            raise InvalidCSVException("Not valid CSV")

        missing = [col for col in self.REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise MissingColumnsException(missing)

        return list(reader)

    def _generate_invitations(self, graduates: list):
        invitations = []
        for graduated in graduates:
            invitation = Invitation(
                full_name=f"{graduated["first_name"]} {graduated["last_name"]}",
                cohort=graduated["cohort"],
                email=graduated["email"],
            )
            invitations.append(invitation)
        return invitations

    def _save_invitations(self, invitations):
        for invitation in invitations:
            self.invitation_repo.save(invitation)

    def _send_invitations(self, invitations: List[Invitation]):
        for invitation in invitations:
            self.email_service.send_invitation(invitation)
