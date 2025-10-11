from fastapi import APIRouter, UploadFile, HTTPException
from fastapi import File, Query, Form


router = APIRouter(
    prefix="/sign-up",
    tags=["sign-up"],
)


@router.get("/invite", status_code=200)
async def check_invitation_token(token: str = Query(...)):
    pass


@router.post("/", status_code=202)
async def sign_up(
    token: str = Query(...),
    github_username: str = Form(...),
    personal_cv: UploadFile = File(...),
    linkedin_cv: UploadFile = File(...),
    avatar_img: UploadFile = File(...),
):

    for file in [personal_cv, linkedin_cv]:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400, detail=f"{file.filename} is not valid PDF"
            )

    if not avatar_img.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail=f"{avatar_img.filename} is not a valid image"
        )
