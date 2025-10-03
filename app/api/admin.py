from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.csv_invitation.csv_invitation import CSVInvitationProcessor

router = APIRouter (
    prefix="/admin",
    tags=["admin"],
)

@router.post("/uploadCSV")
def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    processor = CSVInvitationProcessor()

    try:
        invitations = processor.process_csv(file.file)
    except Exception:
        raise HTTPException(status_code=400)
    
    return {"message": "Invitations processed successfully", "count": len(invitations)}

