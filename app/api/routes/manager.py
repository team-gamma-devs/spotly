# Dependencies
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    status,
    Body,
    Request,
    Query,
)


# General Config
from app.logger import get_logger
from app.settings import settings

# Use Cases
from app.services.use_cases.csv_invitation import CSVInvitationProcessor
from app.services.use_cases.get_filters import GetFilters
from app.services.use_cases.get_invitations import GetInvitations
from app.services.use_cases.graduates_filter import GraduatesFilter
from app.services.use_cases.delete_invitation import DeleteInvitation
from app.services.use_cases.post_feedback import PostFeedback
from app.services.use_cases.delete_feedback import DeleteFeedback

# Schemas
from app.api.schemas.manager_schemas import (
    FiltersListResponse,
    FiltersPayload,
    FilteredUsersResponse,
    FeedbackSchema,
)

# Personalized Exceptions
from app.services.exceptions.csv_invitation_exceptions import (
    InvalidCSVException,
    MissingColumnsException,
)
from app.services.exceptions.delete_user_exceptions import DeleteError
from app.services.exceptions.post_feedback_exceptions import InvalidFeedback

# JWT Verify Decorator
from app.api.decorators.jwt_validation import require_jwt

logger = get_logger(__name__)


router = APIRouter(
    prefix="/manager",
    tags=["manager"],
)


@router.post("/uploadCSV", status_code=status.HTTP_202_ACCEPTED)
# @require_jwt(for_manager=True)
async def upload_csv(
    request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
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


@router.get(
    "/filters", response_model=FiltersListResponse, status_code=status.HTTP_200_OK
)
@require_jwt(for_manager=True)
async def get_filters(request: Request):
    filters = GetFilters()
    return {"filters": await filters.get_available_filters()}


@router.post(
    "/search_graduates",
    response_model=FilteredUsersResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
)
@require_jwt(for_manager=True)
async def search_graduates(
    payload: FiltersPayload = Body(...),
    page: int = Query(1, ge=1, description="Page number starting in 1"),
    pageSize: int = Query(20, ge=1, le=100, description="Number of items per page"),
):
    filters_processor = GraduatesFilter()
    result = await filters_processor.process_filters(payload)
    logger.info(f"{result}")
    return result


##############################################################
##                                                           #
##                       FEEDBACK                            #
##                                                           #
##############################################################


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
@require_jwt(for_manager=True)
async def tutors_feedback(request: Request, payload: FeedbackSchema = Body(...)):
    save_feedback = PostFeedback()
    try:
        save_feedback.save_feedback(payload, request.state.user)
    except InvalidFeedback as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": "Feedback created successfully"}


@router.delete("/feedback", status_code=status.HTTP_204_NO_CONTENT)
@require_jwt(for_manager=True)
async def delete_feedback(request: Request, payload):
    feedback_delete = DeleteFeedback()
    try:
        await feedback_delete.delete(payload)
    except DeleteError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


##############################################################
##                                                           #
##                       INVITATIONS                         #
##                                                           #
##############################################################


@router.post("/invitations", status_code=status.HTTP_200_OK)
@require_jwt(for_manager=True)
async def filter_invitations(request: Request, payload=Body(None)):
    get_inv = GetInvitations()
    invitations = await get_inv.get_all_invitations()
    return invitations


@router.delete("/invitation/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_jwt(for_manager=True)
async def delete_invitation(request: Request, invitation_id: str):
    invitation_delete = DeleteInvitation()
    try:
        await invitation_delete.delete(invitation_id)
    except DeleteError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
