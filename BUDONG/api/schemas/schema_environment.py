from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EnvironmentDataItem(BaseModel):
    data_id: int
    station_id: int
    measurement_time: datetime
    pm10_value: Optional[int] = None
    pm2_5_value: Optional[int] = None
    noise_db: Optional[float] = None


class EnvironmentDataResponse(BaseModel):
    environment_data: List[EnvironmentDataItem]
    latitude: float
    longitude: float