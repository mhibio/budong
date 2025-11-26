from pydantic import BaseModel
from typing import List


class RegionStatsItem(BaseModel):
    stats_id: int
    bjd_code: str
    stats_year: int
    stats_type: str
    stats_value: float


class RegionInfo(BaseModel):
    bjd_code: str
    region_name_full: str


class RegionStatsResponse(BaseModel):
    region_stats: List[RegionStatsItem]
    region: RegionInfo