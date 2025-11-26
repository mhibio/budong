from fastapi import APIRouter
from BUDONG.api.routers.v1 import auth ,search, buildings, reviews, user, environment
router = APIRouter()

# Auth 라우터 등록
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(environment.router, prefix="/environment", tags=["environment"])

@router.get("/")
async def api_root():
    return {"message": "BUDONG API v1"}

