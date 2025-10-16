from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, status

from app.services.csv_invitation.csv_invitation import CSVInvitationProcessor
from app.services.csv_invitation.exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.post("/uploadCSV", status_code=status.HTTP_202_ACCEPTED)
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be CSV"
        )

    contents = await file.read()
    processor = CSVInvitationProcessor()

    try:
        invitations = await processor.process_csv(contents)
        background_tasks.add_task(processor.send_invitations, invitations)
    except InvalidCSVException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except MissingColumnsException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )

    return {"message": "Invitations generated successfully"}
