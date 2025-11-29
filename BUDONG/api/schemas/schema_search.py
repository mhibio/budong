from pydantic import BaseModel, Field
from typing import List, Optional


# 요청 스키마
class SearchPointRequest(BaseModel):
    latitude: float = Field(..., description="검색 중심 위도")
    longitude: float = Field(..., description="검색 중심 경도")
    radius_meters: int = Field(..., ge=1, description="검색 반경 (미터)")


class SearchPointBuilding(BaseModel):
    building_id: int
    bjd_code: Optional[int]
    address: Optional[str]
    building_name: Optional[str]
    building_type: Optional[str]
    build_year: Optional[int]
    total_units: Optional[int]
    latitude: float
    longitude: float


class SearchPointInfra(BaseModel):
    type: str  # "school", "subway_station", "park"
    name: Optional[str]
    address: Optional[str]
    latitude: float
    longitude: float


# 응답 스키마
class SearchPointResponse(BaseModel):
    buildings: List[SearchPointBuilding]
    infrastructure: List[SearchPointInfra]
    search_radius: int
    result_count: int
