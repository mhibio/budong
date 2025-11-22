from fastapi import APIRouter
from BUDONG.api.routers.v1 import auth
from BUDONG.api.routers.v1 import search

router = APIRouter()

# Auth 라우터 등록
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(search.router, prefix="/search", tags=["search"])

@router.get("/")
async def api_root():
    return {"message": "BUDONG API v1"}

