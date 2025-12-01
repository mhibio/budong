from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from BUDONG.api.core.database import get_db
from BUDONG.api.models import (
    TBuilding,
    TRealTransactionPrice,
    TBuildingReview,
    TSchool,
    TPark,
    TStation,
    TPoliceStationInfo,
    TCrimeCCTV,
    TPublicTransportByAdminDong,
    TBjdTable,
    TJcgBjdTable,
    TNoise,
    TCCTVInfo
)

from BUDONG.api.schemas.schema_buildings import (
    BuildingRequest,
    BuildingDetailResponse,
    BuildingDetail,
    BuildingTransaction,
    BuildingReview as ReviewSchema,
    NearbyInfrastructure,
    RegionStat,
    EnvironmentData,
)

from BUDONG.util.geoutil import haversine

router = APIRouter()


@router.post("/detail", response_model=BuildingDetailResponse)
def get_building_detail(
    payload: BuildingRequest,
    db: Session = Depends(get_db)
):

    # ------------------------------------------------------------------
    # 1. 건물 정보 조회
    # ------------------------------------------------------------------
    building = (
        db.query(TBuilding)
        .filter(TBuilding.building_id == payload.building_id)
        .first()
    )

    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    b_lat = building.lat
    b_lon = building.lon

    building_schema = BuildingDetail(
        building_id=building.building_id,
        bjd_code=building.bjd_code,
        address=building.address,
        building_name=building.building_name,
        building_type=building.building_type,
        build_year=building.build_year,
        total_units=building.total_units,
        latitude=b_lat,
        longitude=b_lon,
    )

    # ------------------------------------------------------------------
    # 2. 실거래가 정보
    # ------------------------------------------------------------------
    tx_list = (
        db.query(TRealTransactionPrice)
        .filter(TRealTransactionPrice.building_id == building.building_id)
        .all()
    )

    transactions_schema = [
        BuildingTransaction(
            tx_id=tx.tx_id,
            building_id=tx.building_id,
            transaction_date=tx.transaction_date,
            price=tx.price,
            area_sqm=tx.area_sqm,
            floor=tx.floor,
        )
        for tx in tx_list
    ][:10]

    # ------------------------------------------------------------------
    # 3. 리뷰 정보
    # ------------------------------------------------------------------
    review_list = (
        db.query(TBuildingReview)
        .filter(TBuildingReview.building_id == building.building_id)
        .all()
    )

    reviews_schema = [
        ReviewSchema(
            review_id=r.review_id,
            user_id=r.user_id,
            building_id=r.building_id,
            rating=r.rating,
            content=r.content,
            created_at=r.created_at,
        )
        for r in review_list
    ]


    # ------------------------------------------------------------------
    # 4. 주변 인프라 (학교, 공원, 지하철)
    # ------------------------------------------------------------------
    INFRA_RADIUS_M = 1000
    infra_schema = []

    # ------ 학교 ------
    schools = db.query(TSchool).all()
    for s in schools:
        if s.lat is None or s.lon is None:
            continue

        dist = haversine(b_lat, b_lon, s.lat, s.lon)
        if dist <= INFRA_RADIUS_M:
            infra_schema.append(
                NearbyInfrastructure(
                    infra_id=str(s.school_id),
                    infra_category="school",
                    name=s.school_name,
                    address=s.address,
                    latitude=s.lat,
                    longitude=s.lon,
                )
            )

    # ------ 공원 ------
    parks = db.query(TPark).all()
    for p in parks:
        if p.lat is None or p.lon is None:
            continue

        dist = haversine(b_lat, b_lon, p.lat, p.lon)
        if dist <= INFRA_RADIUS_M:
            infra_schema.append(
                NearbyInfrastructure(
                    infra_id=p.park_name,
                    infra_category="park",
                    name=p.park_name,
                    address=p.address,
                    latitude=p.lat,
                    longitude=p.lon,
                )
            )

    # ------ 지하철역 ------
    stations = db.query(TStation).all()
    for st in stations:
        if st.lat is None or st.lon is None:
            continue

        dist = haversine(b_lat, b_lon, st.lat, st.lon)
        if dist <= INFRA_RADIUS_M:
            st_complexity = db.query(TPublicTransportByAdminDong).filter(TPublicTransportByAdminDong.station_id == st.station_id).first()
            ext = None
            if st_complexity != None:
                ext = {
                    "passenger_num":st_complexity.passenger_num * 80, # 80으로 나눠진 평균값이므로 실 인원수는 80
                    "complexity_rating":st_complexity.complexity_rating
                }

            infra_schema.append(
                NearbyInfrastructure(
                    infra_id=str(st.station_id),
                    infra_category="subway_station",
                    name=st.station_name,
                    address=None,
                    latitude=st.lat,
                    longitude=st.lon,
                    extra_data=ext
                )
            )

    # ------------------------------------------------------------------
    # 5. 경찰서 정보 (법정동 → bjd_name 기반)
    # ------------------------------------------------------------------
    # police = None

    # if building.bjd_code:
    #     bjd = db.query(TBjdTable).filter(TBjdTable.bjd_code == building.bjd_code).first()

    #     if bjd and bjd.bjd_name:
    #         police = (
    #             db.query(TPoliceStationInfo)
    #             .filter(TPoliceStationInfo.bjd_name == bjd.bjd_name)
    #             .first()
    #         )

    # if police:
    #     infra_schema.append(
    #         NearbyInfrastructure(
    #             infra_id=police.polic_station_name,
    #             infra_category="public_office",
    #             name=police.polic_station_name,
    #             address=police.address,
    #             latitude=None,
    #             longitude=None,
    #         )
    #     )

    # ------------------------------------------------------------------
    # 6. 범죄/CCTV 정보 (자치구)
    # ------------------------------------------------------------------
    crime = None
    region_name = None
    jcg_name = building.address.split(' ')[0]
    region_name = jcg_name
    print()

    crime = (
        db.query(TCrimeCCTV)
        .filter(TCrimeCCTV.jcg_name == region_name)
        .first()
    )

    # if crime:
    #     infra_schema.append(
    #         NearbyInfrastructure(
    #             infra_id=crime.jcg_name,
    #             infra_category="cctv",
    #             name=crime.jcg_name,
    #             address=None,
    #             latitude=None,
    #             longitude=None,
    #             extra_data={
    #                 "crime_num": crime.crime_num,
    #                 "cctv_num": crime.cctv_num,
    #                 "dangerous_rating": crime.dangerous_rating,
    #                 "cctv_security_rating": crime.CCTV_security_rating,
    #             }
    #         )
    #     )

    # ------------------------------------------------------------------
    # 7. 지역 통계 (범죄지표 + 복잡도)
    # ------------------------------------------------------------------
    
    # cctv
    print(b_lon, b_lat)
    radius_m = 1000
    distance_expression = func.ST_Distance_Sphere(
        func.Point(TCCTVInfo.lon, TCCTVInfo.lat),  
        func.Point(b_lon, b_lat)
    )

    # 3. 쿼리 작성: 거리가 radius_m 이하인 항목의 cnt 합계를 구합니다.
    cctv_list = db.query(TCCTVINFO).filter(distance_expression <= radius_m)

    # total_cnt = int(total_count) if total_count is not None else 0
    # print(total_cnt)

    region_stats = []

    # 범죄지표
    crime_stat = {
        "crime_num": crime.crime_num if crime else None,
        "cctv_num": crime.cctv_num if crime else None,
        "dangerous_rating": crime.dangerous_rating if crime else None,
        # "cctv_security_rating": crime.CCTV_security_rating if crime else None,
    }


    region_stats.append(
        RegionStat(
            region_name=region_name,
            crime_num=crime_stat["crime_num"],
            cctv_num=crime_stat["cctv_num"],
            dangerous_rating=crime_stat["dangerous_rating"],
            cctv_security_rating=crime_stat["cctv_security_rating"],
            real_cctv=cctv_list
        )
    )


    # ------------------------------------------------------------------
    # 8. 환경 데이터 (가장 가까운 noise 지점 1개)
    # ------------------------------------------------------------------
    noise_list = db.query(TNoise).all()

    nearest_noise = None
    min_dist = float("inf")

    for n in noise_list:
        if n is None:
            continue
        if n.lat is None or n.lon is None:
            continue

        dist = haversine(b_lat, b_lon, n.lat, n.lon)
        if dist < min_dist:
            min_dist = dist
            nearest_noise = n

    environment_schema = []

    if nearest_noise:
        environment_schema.append(
            EnvironmentData(
                address=nearest_noise.address,
                noise_max=nearest_noise.noise_max,
                noise_avg=nearest_noise.noise_avg,
                noise_min=nearest_noise.noise_min,
                latitude=nearest_noise.lat,
                longitude=nearest_noise.lon,
            )
        )

    # ------------------------------------------------------------------
    # 최종 반환
    # ------------------------------------------------------------------
    return BuildingDetailResponse(
        building=building_schema,
        transactions=transactions_schema,
        reviews=reviews_schema,
        nearby_infrastructure=infra_schema,
        region_stats=region_stats,
        environment_data=environment_schema,
    )
