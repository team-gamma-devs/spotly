# Dependencies
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    status,
    Body,
)

# General Config
from app.settings import settings

# Use Cases
from app.services.use_cases.csv_invitation import CSVInvitationProcessor
from app.services.use_cases.get_filters import GetFilters
from app.services.use_cases.graduates_filter import GraduatesFilter

# Schemas
from app.api.schemas.manager_schemas import (
    FiltersListResponse,
    FiltersPayload,
    FilteredUsers,
)

# Personalized Exceptions
from app.services.exceptions.csv_invitation_exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)

# JWT Verify Decorator
from app.api.decorators.jwt_validation import require_jwt

router = APIRouter(
    prefix="/manager",
    tags=["manager"],
)


# @require_jwt(for_manager=True)
@router.post("/uploadCSV", status_code=status.HTTP_202_ACCEPTED)
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    MAX_CSV_SIZE_BYTES = settings.max_csv_size * 1024 * 1024

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be CSV"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_CSV_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"{file.filename} exceeds {settings.max_csv_size:.1f}MB limit",
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


# @require_jwt(for_manager=True)
@router.post("/invitations", status_code=status.HTTP_200_OK)
async def filter_invitations():

    pass


# @require_jwt(for_manager=True)
@router.get(
    "/filters", response_model=FiltersListResponse, status_code=status.HTTP_200_OK
)
async def get_filters():
    filters = GetFilters()
    return {"filters": await filters.get_available_filters()}


# @require_jwt(for_manager=True)
@router.post(
    "/search_graduates",
    response_model=FilteredUsers,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
async def search_graduates(payload: FiltersPayload = Body(...)):
    filters_processor = GraduatesFilter()
    result = await filters_processor.process_filters(payload)
    return result


# @require_jwt(for_manager=True)
@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def tutors_feedback():
    pass
