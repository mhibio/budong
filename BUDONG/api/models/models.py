from sqlalchemy import Column, Integer, String, DateTime, Text, DECIMAL, BIGINT, Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from BUDONG.api.core.database import Base
from BUDONG.api.models.enums.infra_category import InfraCategory
from BUDONG.api.models.enums.stats_type import StatsType
from BUDONG.api.models.enums.station_type import StationType
from BUDONG.api.models.enums.user_role import UserRole


# --------------------------------------
# 1. 사용자 및 활동 테이블
# --------------------------------------

class TUser(Base):
    __tablename__ = "t_user"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="회원 ID")
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.USER.value, comment="사용자 역할: user, admin")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    reviews = relationship("TBuildingReview", back_populates="user")
    saved_buildings = relationship("TUserSavedBuilding", back_populates="user")


class TBuildingReview(Base):
    __tablename__ = "t_building_review"
    
    review_id = Column(Integer, primary_key=True, autoincrement=True, comment="리뷰 ID")
    user_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="작성자 ID")
    building_id = Column(Integer, ForeignKey("t_building.building_id"), nullable=False, comment="건물 ID")
    rating = Column(Integer, nullable=False, comment="평점 (1~5)")
    content = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("TUser", back_populates="reviews")
    building = relationship("TBuilding", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index("idx_review_user_id", "user_id"),
        Index("idx_review_building_id", "building_id"),
    )


class TUserSavedBuilding(Base):
    __tablename__ = "t_user_saved_building"
    
    save_id = Column(Integer, primary_key=True, autoincrement=True, comment="찜 ID")
    user_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="회원 ID")
    building_id = Column(Integer, ForeignKey("t_building.building_id"), nullable=False, comment="건물 ID")
    memo = Column(String(255), comment="간단 메모")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("TUser", back_populates="saved_buildings")
    building = relationship("TBuilding", back_populates="saved_by_users")
    
    # Indexes - 한 유저가 한 건물을 중복 찜 방지
    __table_args__ = (
        UniqueConstraint("user_id", "building_id", name="uq_user_building"),
        Index("idx_saved_user_id", "user_id"),
        Index("idx_saved_building_id", "building_id"),
    )


# --------------------------------------
# 2. 부동산 및 인프라 (Point 데이터)
# --------------------------------------

class TBuilding(Base):
    __tablename__ = "t_building"
    
    building_id = Column(Integer, primary_key=True, autoincrement=True, comment="건물 ID")
    bjd_code = Column(String(10), ForeignKey("t_region.bjd_code"), nullable=False, comment="법정동 코드")
    address = Column(String(255), comment="도로명주소")
    building_name = Column(String(100), comment="예: 래미안아파트")
    building_type = Column(String(50), comment="예: 아파트, 오피스텔")
    build_year = Column(Integer, comment="준공연도")
    total_units = Column(Integer, comment="총 세대수")
    # MySQL Spatial: GEOMETRY 타입 사용 (실제 DB에서는 GEOMETRY로 생성)
    # SQLAlchemy에서는 Text로 저장하고, 애플리케이션에서 WKT 형식으로 처리
    location = Column(Text, nullable=False, comment="Spatial POINT Type (WKT 형식: POINT(lon lat))")
    
    # Relationships
    region = relationship("TRegion", back_populates="buildings")
    reviews = relationship("TBuildingReview", back_populates="building")
    saved_by_users = relationship("TUserSavedBuilding", back_populates="building")
    transactions = relationship("TRealEstateTransaction", back_populates="building")
    
    # Indexes
    __table_args__ = (
        Index("idx_building_bjd_code", "bjd_code"),
    )


class TRealEstateTransaction(Base):
    __tablename__ = "t_real_estate_transaction"
    
    tx_id = Column(Integer, primary_key=True, autoincrement=True, comment="거래 ID")
    building_id = Column(Integer, ForeignKey("t_building.building_id"), nullable=False, comment="건물 ID")
    transaction_date = Column(Date, nullable=False)
    price = Column(BIGINT, nullable=False, comment="거래금액 (만원단위)")
    area_sqm = Column(DECIMAL(10, 2), nullable=False, comment="전용면적 ㎡")
    floor = Column(Integer)
    
    # Relationships
    building = relationship("TBuilding", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index("idx_tx_building_id", "building_id"),
        Index("idx_tx_date", "transaction_date"),
    )


class TInfrastructure(Base):
    __tablename__ = "t_infrastructure"
    
    infra_id = Column(Integer, primary_key=True, autoincrement=True, comment="인프라 ID")
    infra_category = Column(String(20), nullable=False, comment="Enum: school, park, subway_station, bus_stop, hospital, mart, bank, public_office, cctv")
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    # MySQL Spatial: GEOMETRY 타입 사용
    location = Column(Text, nullable=False, comment="Spatial POINT Type (WKT 형식: POINT(lon lat))")
    
    # Relationships
    school_detail = relationship("TSchoolDetail", back_populates="infrastructure", uselist=False)
    park_detail = relationship("TParkDetail", back_populates="infrastructure", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_infra_category", "infra_category"),
    )


class TSchoolDetail(Base):
    __tablename__ = "t_school_detail"
    
    infra_id = Column(Integer, ForeignKey("t_infrastructure.infra_id"), primary_key=True, comment="인프라 ID (T_INFRA PK와 동일)")
    school_type = Column(String(20), comment="예: 초, 중, 고, 특수")
    assigned_district = Column(Text, comment="초등학교 통학구역 정보")
    
    # Relationships
    infrastructure = relationship("TInfrastructure", back_populates="school_detail")


class TParkDetail(Base):
    __tablename__ = "t_park_detail"
    
    infra_id = Column(Integer, ForeignKey("t_infrastructure.infra_id"), primary_key=True, comment="인프라 ID (T_INFRA PK와 동일)")
    park_type = Column(String(50), comment="예: 근린공원, 어린이공원")
    area_sqm = Column(DECIMAL(10, 2), comment="공원 면적")
    
    # Relationships
    infrastructure = relationship("TInfrastructure", back_populates="park_detail")


# --------------------------------------
# 3. 지역 기반 (Polygon 데이터)
# --------------------------------------

class TRegion(Base):
    __tablename__ = "t_region"
    
    bjd_code = Column(String(10), primary_key=True, comment="법정동 코드")
    region_name_full = Column(String(100), comment="예: 서울특별시 강남구 역삼동")
    # MySQL Spatial: GEOMETRY 타입 사용
    region_polygon = Column(Text, nullable=False, comment="Spatial POLYGON Type (WKT 형식)")
    
    # Relationships
    buildings = relationship("TBuilding", back_populates="region")
    stats = relationship("TRegionStats", back_populates="region")


class TRegionStats(Base):
    __tablename__ = "t_region_stats"
    
    stats_id = Column(Integer, primary_key=True, autoincrement=True)
    bjd_code = Column(String(10), ForeignKey("t_region.bjd_code"), nullable=False, comment="법정동 코드")
    stats_year = Column(Integer, nullable=False)
    stats_type = Column(String(30), nullable=False, comment="Enum: crime_total, crime_theft, noise_day, noise_night")
    stats_value = Column(DECIMAL(10, 2), comment="통계 값")
    
    # Relationships
    region = relationship("TRegion", back_populates="stats")
    
    # Indexes - 특정 년도, 특정 타입의 통계는 지역별로 하나
    __table_args__ = (
        UniqueConstraint("bjd_code", "stats_year", "stats_type", name="uq_region_stats"),
        Index("idx_stats_bjd_code", "bjd_code"),
    )


class TEnvironmentStation(Base):
    __tablename__ = "t_environment_station"
    
    station_id = Column(Integer, primary_key=True, autoincrement=True, comment="측정소 ID")
    station_type = Column(String(20), nullable=False, comment="Enum: air_quality, noise")
    station_name = Column(String(100))
    # MySQL Spatial: GEOMETRY 타입 사용
    location = Column(Text, nullable=False, comment="Spatial POINT Type (WKT 형식: POINT(lon lat))")
    
    # Relationships
    environment_data = relationship("TEnvironmentData", back_populates="station")
    
    # Indexes
    __table_args__ = (
        Index("idx_station_type", "station_type"),
    )


class TEnvironmentData(Base):
    __tablename__ = "t_environment_data"
    
    data_id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey("t_environment_station.station_id"), nullable=False, comment="측정소 ID")
    measurement_time = Column(DateTime, nullable=False)
    pm10_value = Column(Integer, comment="미세먼지")
    pm2_5_value = Column(Integer, comment="초미세먼지")
    noise_db = Column(DECIMAL(5, 1), comment="소음")
    
    # Relationships
    station = relationship("TEnvironmentStation", back_populates="environment_data")
    
    # Indexes
    __table_args__ = (
        Index("idx_env_station_time", "station_id", "measurement_time"),
    )
