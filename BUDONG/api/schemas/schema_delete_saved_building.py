from pydantic import BaseModel

class DeleteSavedBuildingRequest(BaseModel):
    save_id: int

class DeleteSavedBuildingResponse(BaseModel):
    success: bool
    message: str
