from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.csv_invitation.csv_invitation import CSVInvitationProcessor
from app.services.csv_invitation.exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.post("/uploadCSV", status_code=202)
def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV")

    processor = CSVInvitationProcessor()

    try:
        processor.process_csv(file.file)
    except InvalidCSVException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MissingColumnsException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Invitations generated successfully"}
