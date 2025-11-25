from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models import TUserSavedBuilding
from BUDONG.api.schemas.schema_delete_saved_building import (
    DeleteSavedBuildingRequest,
    DeleteSavedBuildingResponse
)

router = APIRouter()

@router.delete("/delete-saved-building", response_model=DeleteSavedBuildingResponse)
def delete_saved_building(request: DeleteSavedBuildingRequest, db: Session = Depends(get_db)):
    saved = db.query(TUserSavedBuilding).filter(TUserSavedBuilding.save_id == request.save_id).first()

    if not saved:
        raise HTTPException(status_code=404, detail="해당 save_id가 존재하지 않습니다.")

    db.delete(saved)
    db.commit()

    return {"success": True, 
            "message": "성공"}
