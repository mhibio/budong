from fastapi import APIRouter
from BUDONG.api.routers.v1.user import saved_buildings, save_buildings, delete_saved_building

router = APIRouter()

# 각 라우터 등록
router.include_router(saved_buildings.router, tags=["user"])
router.include_router(save_buildings.router, tags=["user"])
router.include_router(delete_saved_building.router, tags=["user"])