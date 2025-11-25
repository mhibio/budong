from fastapi import APIRouter
from BUDONG.api.routers.v1 import auth
from BUDONG.api.routers.v1 import search
from BUDONG.api.routers.v1 import buildings
from BUDONG.api.routers.v1.reviews import get_reviews
from BUDONG.api.routers.v1.reviews import create_review
from BUDONG.api.routers.v1.user.saved_buildings import router as saved_buildings_router
from BUDONG.api.routers.v1.user.save_buildings import router as save_buildings_router
from BUDONG.api.routers.v1.user.delete_saved_building import router as delete_saved_building_router
router = APIRouter()

# Auth 라우터 등록
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
router.include_router(get_reviews.router, prefix="/reviews",tags=["reviews"])
router.include_router(create_review.router, prefix="/reviews", tags=["reviews"])
router.include_router(saved_buildings_router, prefix="/user", tags=["user"])
router.include_router(save_buildings_router, prefix="/user", tags=["user"])
router.include_router(delete_saved_building_router, prefix="/user", tags=["user"])
@router.get("/")
async def api_root():
    return {"message": "BUDONG API v1"}

