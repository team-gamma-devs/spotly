import csv

from app.domain.invitation import Invitation
from .exceptions import InvalidCSVException, MissingColumnsException


class CSVInvitationProcessor:
    REQUIRED_COLUMNS = ["first_name", "last_name", "cohort", "email"]

    def __init__(self, invitation_repo, email_service):
        self.invitation_repo = invitation_repo
        self.email_service = email_service

    def process_csv(self, file):
        """Orquesta todo el flujo de validación, creación, guardado y envío"""
        df = self._validate_csv(file)
        invitations = self._generate_invitations(df)
        self._save_invitations(invitations)
        self._send_invitations(invitations)
        return invitations

    # -------------------------
    # Métodos privados helpers
    # -------------------------

    def _validate_csv(self, file):
        """Verifica extensión y columnas requeridas"""
        if not file.name.endswith(".csv"):
            raise InvalidCSVException("El archivo debe ser un CSV")

        file.seek(0)
        reader = csv.DictReader(file.read().decode("utf-8").splitlines())

        missing = [col for col in self.REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise MissingColumnsException(missing)

        return list(reader)

    def _generate_invitations(self, rows):
        invitations = []
        for row in rows:
            invitation = Invitation(
                full_name=f"{row["first_name"]} {row["last_name"]}",
                cohort=row["cohort"],
                email=row["email"],
            )
            invitations.append(invitation)
        return invitations

    def _save_invitations(self, invitations):
        for invitation in invitations:
            self.invitation_repo.save(invitation)

    def _send_invitations(self, invitations):
        for invitation in invitations:
            self.email_service.send_invitation(invitation)
