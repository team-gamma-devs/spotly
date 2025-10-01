from fastapi import APIRouter, UploadFile, HTTPException

from app.services.csv_invitation.csv_invitation import CSVInvitationProcessor

router = APIRouter (
    prefix="/admin",
    tags=["admin"],
)

@router.post("/uploadCSV")
def upload_csv(file: UploadFile):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    use_case = CSVInvitationProcessor()
    return 201
