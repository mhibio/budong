from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import (
    TEnvironmentStation,
    TEnvironmentData,
)

from BUDONG.api.schemas.schema_environment import (
    EnvironmentDataItem,
    EnvironmentDataResponse,
)

from BUDONG.util.geoutil import parse_wkt_point, haversine

router = APIRouter()


@router.get("/data", response_model=EnvironmentDataResponse)
def get_environment_data(
    latitude: float = Query(...),
    longitude: float = Query(...),
    db: Session = Depends(get_db)
):
    """
    특정 좌표 주변 관측소 데이터를 조회
    """


    # 모든 측정소 목록 조회
    stations = db.query(TEnvironmentStation).all()
    if not stations:
        raise HTTPException(status_code=404, detail="측정소 데이터가 없습니다.")

    # 입력 좌표와 가장 가까운 측정소 찾기
    nearest_station = None
    nearest_distance = float("inf")

    for st in stations:
        st_lat, st_lon = parse_wkt_point(st.location)
        dist = haversine(b_lat, b_lon, st_lat, st_lon)

        if dist < nearest_distance:
            nearest_distance = dist
            nearest_station = st

    if nearest_station is None:
        raise HTTPException(status_code=404, detail="근처에 사용 가능한 측정소가 없습니다.")

    # 해당 측정소의 환경 데이터 조회
    env_list = (
        db.query(TEnvironmentData)
        .filter(TEnvironmentData.station_id == nearest_station.station_id)
        .order_by(TEnvironmentData.measurement_time.desc())
        .all()
    )

    environment_data_schema = [
        EnvironmentDataItem(
            data_id=e.data_id,
            station_id=e.station_id,
            measurement_time=e.measurement_time,
            pm10_value=e.pm10_value,
            pm2_5_value=e.pm2_5_value,
            noise_db=float(e.noise_db) if e.noise_db is not None else None,
        )
        for e in env_list
    ]

    return EnvironmentDataResponse(
        environment_data=environment_data_schema,
        latitude=latitude,
        longitude=longitude,
    )
