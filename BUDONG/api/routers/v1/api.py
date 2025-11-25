from fastapi import APIRouter
from BUDONG.api.routers.v1 import auth
from BUDONG.api.routers.v1 import search
from BUDONG.api.routers.v1 import buildings
from BUDONG.api.routers.v1.reviews import get_reviews
router = APIRouter()

# Auth 라우터 등록
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
router.include_router(get_reviews.router, tags=["reviews"])
@router.get("/")
async def api_root():
    return {"message": "BUDONG API v1"}

