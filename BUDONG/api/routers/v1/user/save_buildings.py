from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models import TUserSavedBuilding
from BUDONG.api.schemas.schema_save_building import SaveBuildingRequest, SaveBuildingResponse

router = APIRouter()  # <-- Good!

@router.post("/save-building", response_model=SaveBuildingResponse)
def save_building(request: SaveBuildingRequest, db: Session = Depends(get_db)):
    # 1️⃣ Check if already saved (prevent duplicate)
    existing = db.query(TUserSavedBuilding).filter(
        TUserSavedBuilding.user_id == 1,
        TUserSavedBuilding.building_id == request.building_id
    ).first()

    if existing:
        return {
            "success": False,
            "save_id": existing.save_id,
            "building_id": request.building_id,
            "message": "이미 찜한 건물입니다!"  # No error anymore
        }

    # 2️⃣ If not exist → insert
    new_saved = TUserSavedBuilding(
        user_id=1,
        building_id=request.building_id,
        memo=request.memo
    )
    db.add(new_saved)
    db.commit()
    db.refresh(new_saved)

    return {
        "success": True,
        "save_id": new_saved.save_id,
        "building_id": request.building_id,
        "message": "찜하기 완료!"
    }
