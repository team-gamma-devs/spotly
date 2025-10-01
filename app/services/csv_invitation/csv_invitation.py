from fastapi import HTTPException
from app.domain.invitation import Invitation

REQUIRED_COLUMNS = ["first_name", "last_name", "cohort", "email"]


# Esto esta todo roto
class CSVInvitationProcessor:
    def __init__(self, invitation_repo: InvitationRepository, email_service: EmailService):
        self.invitation_repo = invitation_repo
        self.email_service = email_service

    def validate_csv(self, file) -> pd.DataFrame:
        """Valida que el CSV tenga las columnas requeridas y lo carga en un DataFrame"""
        df = pd.read_csv(file)
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Faltan columnas requeridas: {missing}"
            )
        return df

    def process_csv(self, file):
        """Procesa el CSV completo: validación, creación de invitaciones y envío"""
        df = self.validate_csv(file)
        invitations = []

        for _, row in df.iterrows():
            # 1. Crear la invitación usando el modelo de dominio
            invitation = Invitation(
                name=row["nombre"],
                email=row["email"],
                phone=row["telefono"],
            )

            # 2. Guardar en la base de datos
            self.invitation_repo.save(invitation)

            # 3. Enviar la invitación por email
            self.email_service.send_invitation(invitation)

            invitations.append(invitation)

        # 4. Devolver un resumen en JSON si se quiere
        return [inv.to_dict() for inv in invitations]
