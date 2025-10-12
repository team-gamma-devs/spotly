from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks

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
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV")

    contents = await file.read()
    processor = CSVInvitationProcessor()

    try:
        invitations = processor.process_csv(contents)
        background_tasks.add_task(processor.send_invitations, invitations)
    except InvalidCSVException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MissingColumnsException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Invitations generated successfully"}
