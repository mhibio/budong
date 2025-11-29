from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from BUDONG.api.core.database import get_db
from BUDONG.api.models.models import (
    TBuilding, TSchool, TStation, TPark
)
from BUDONG.api.schemas.schema_search import (
    SearchPointRequest,
    SearchPointResponse,
    SearchPointBuilding,
    SearchPointInfra
)
from BUDONG.util.geoutil import haversine

router = APIRouter()


@router.post("/point", response_model=SearchPointResponse)
def search_point(
    payload: SearchPointRequest,
    db: Session = Depends(get_db)
):

    lat = payload.latitude
    lon = payload.longitude
    radius = payload.radius_meters

    # ================================
    # 1. 건물 조회
    # ================================
    buildings = db.query(TBuilding).all()

    result_buildings = []
    for b in buildings:
        if b.lat is None or b.lon is None:
            continue

        dist = haversine(lat, lon, b.lat, b.lon)

        if dist <= radius:
            result_buildings.append(
                SearchPointBuilding(
                    building_id=b.building_id,
                    bjd_code=b.bjd_code,
                    address=b.address,
                    building_name=b.building_name,
                    building_type=b.building_type,
                    build_year=b.build_year,
                    total_units=b.total_units,
                    latitude=b.lat,
                    longitude=b.lon
                )
            )

    # ================================
    # 2. 인프라 조회 (학교 + 역 + 공원)
    # ================================
    infra_results = []

    # --- 학교 ---
    schools = db.query(TSchool).all()
    for s in schools:
        if s.lat is None or s.lon is None:
            continue

        dist = haversine(lat, lon, s.lat, s.lon)
        if dist <= radius:
            infra_results.append(
                SearchPointInfra(
                    type="school",
                    name=s.school_name,
                    address=s.address,
                    latitude=s.lat,
                    longitude=s.lon
                )
            )

    # --- 지하철역 ---
    stations = db.query(TStation).all()
    for st in stations:
        if st.lat is None or st.lon is None:
            continue

        dist = haversine(lat, lon, st.lat, st.lon)
        if dist <= radius:
            infra_results.append(
                SearchPointInfra(
                    type="subway_station",
                    name=st.station_name,
                    address=None,
                    latitude=st.lat,
                    longitude=st.lon
                )
            )

    # --- 공원 ---
    parks = db.query(TPark).all()
    for p in parks:
        if p.lat is None or p.lon is None:
            continue

        dist = haversine(lat, lon, p.lat, p.lon)
        if dist <= radius:
            infra_results.append(
                SearchPointInfra(
                    type="park",
                    name=p.park_name,
                    address=p.address,
                    latitude=p.lat,
                    longitude=p.lon
                )
            )

    return SearchPointResponse(
        buildings=result_buildings,
        infrastructure=infra_results,
        search_radius=radius,
        result_count=len(result_buildings) + len(infra_results)
    )
