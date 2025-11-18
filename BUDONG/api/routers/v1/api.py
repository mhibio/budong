from fastapi import APIRouter
from BUDONG.api.routers.v1 import auth

router = APIRouter()

# Auth 라우터 등록
router.include_router(auth.router, prefix="/auth", tags=["auth"])


@router.get("/")
async def api_root():
    return {"message": "BUDONG API v1"}

