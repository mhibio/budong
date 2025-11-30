from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models import TUser, TUserSavedBuilding
from BUDONG.api.core.auth import get_current_active_user
from BUDONG.api.schemas.schema_saved_buildings import SavedBuildingsResponse

router = APIRouter()

@router.get("/saved-buildings", response_model=SavedBuildingsResponse)
def get_saved_buildings(
    db: Session = Depends(get_db),
    current_user: TUser = Depends(get_current_active_user)  # 🔥 Token-based user
):
    saved_buildings = (
        db.query(TUserSavedBuilding)
        .filter(TUserSavedBuilding.user_id == current_user.user_id)  # 💯 real user
        .all()
    )

    return {
        "saved_buildings": saved_buildings,
        "total_count": len(saved_buildings)
    }
