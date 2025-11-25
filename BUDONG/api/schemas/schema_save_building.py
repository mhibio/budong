from pydantic import BaseModel

class SaveBuildingRequest(BaseModel):
    building_id: int
    memo: str | None = None

class SaveBuildingResponse(BaseModel):
    success: bool
    save_id: int
    building_id: int
    message: str
