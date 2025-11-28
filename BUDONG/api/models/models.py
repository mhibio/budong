"""
SQLAlchemy ORM Models for AreaPulse DB
Database: areapulsedb (MySQL 8.0)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger, Integer, String, Text, Float, DateTime, 
    SmallInteger, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# =====================================================
# 1. 사용자 및 활동 테이블
# =====================================================

class TUser(Base):
    __tablename__ = "t_user"
    __table_args__ = {"comment": "사용자 계정 정보"}

    user_id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="회원 ID"
    )
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    nickname: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.now
    )

    # Relationships
    reviews: Mapped[list["TBuildingReview"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    saved_buildings: Mapped[list["TUserSavedBuilding"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )


class TBuildingReview(Base):
    __tablename__ = "t_building_review"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_building_id", "building_id"),
        {"comment": "건물 리뷰 정보"}
    )

    review_id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="리뷰 ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_user.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="작성자 ID"
    )
    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_building.building_id", ondelete="CASCADE"),
        nullable=False,
        comment="건물 ID"
    )
    rating: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="평점 (1~5)"
    )
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now
    )

    # Relationships
    user: Mapped["TUser"] = relationship(back_populates="reviews")
    building: Mapped["TBuilding"] = relationship(back_populates="reviews")


class TUserSavedBuilding(Base):
    __tablename__ = "t_user_saved_building"
    __table_args__ = (
        UniqueConstraint("user_id", "building_id", name="uk_user_building"),
        {"comment": "사용자 찜 목록"}
    )

    save_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="찜 ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("t_user.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="회원 ID"
    )
    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_building.building_id", ondelete="CASCADE"),
        nullable=False,
        comment="건물 ID"
    )
    memo: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="간단 메모"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now
    )

    # Relationships
    user: Mapped["TUser"] = relationship(back_populates="saved_buildings")
    building: Mapped["TBuilding"] = relationship(back_populates="saved_by_users")


# =====================================================
# 2. 지역 및 건물 테이블
# =====================================================

class TBjdTable(Base):
    __tablename__ = "t_bjd_table"

    bjd_code: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="법정동 코드"
    )
    bjd_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bjd_eng: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    buildings: Mapped[list["TBuilding"]] = relationship(back_populates="bjd")
    jcg_mappings: Mapped[list["TJcgBjdTable"]] = relationship(back_populates="bjd")


class TBuilding(Base):
    __tablename__ = "t_building"
    __table_args__ = (
        Index("idx_bjd_code", "bjd_code"),
    )

    building_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="건물 ID"
    )
    bjd_code: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("t_bjd_table.bjd_code", ondelete="SET NULL"),
        nullable=True,
        comment="법정동 코드"
    )
    address: Mapped[str] = mapped_column(Text, nullable=False)
    building_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    building_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    build_year: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_units: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    bjd: Mapped[Optional["TBjdTable"]] = relationship(back_populates="buildings")
    reviews: Mapped[list["TBuildingReview"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan"
    )
    saved_by_users: Mapped[list["TUserSavedBuilding"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[list["TRealTransactionPrice"]] = relationship(
        back_populates="building",
        cascade="all, delete-orphan"
    )


# =====================================================
# 3. 거래 정보 테이블
# =====================================================

class TRealTransactionPrice(Base):
    __tablename__ = "t_real_transaction_price"
    __table_args__ = (
        Index("idx_building_id", "building_id"),
        Index("idx_transaction_date", "transaction_date"),
    )

    tx_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="거래 ID"
    )
    building_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("t_building.building_id", ondelete="CASCADE"),
        nullable=False,
        comment="건물 ID"
    )
    transaction_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    area_sqm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    floor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    building: Mapped["TBuilding"] = relationship(back_populates="transactions")


# =====================================================
# 4. 안전 및 치안 정보
# =====================================================

class TCrimeCCTV(Base):
    __tablename__ = "t_crime_CCTV"

    jcg_name: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        comment="자치구명"
    )
    crime_num: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    cctv_num: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    dangerous_rating: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    CCTV_security_rating: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)


class TPoliceStationInfo(Base):
    __tablename__ = "t_police_station_info"

    polic_station_name: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        comment="경찰서명"
    )
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bjd_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# =====================================================
# 5. 교통 및 시설 정보
# =====================================================

class TStation(Base):
    __tablename__ = "t_station"

    station_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="역 ID"
    )
    line: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    station_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class TPublicTransportByAdminDong(Base):
    __tablename__ = "t_public_transport_by_admin_dong"

    hjd_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        comment="행정동 ID"
    )
    passenger_num: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    complexity_rating: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)


class TSchool(Base):
    __tablename__ = "t_school"
    __table_args__ = (
        Index("idx_school_name", "school_name"),
    )

    school_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="학교 ID"
    )
    school_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    build_year: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    ja_chi_gu: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    school_level: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class TPark(Base):
    __tablename__ = "t_park"

    park_name: Mapped[str] = mapped_column(
        String(200),
        primary_key=True,
        comment="공원명"
    )
    park_introduce: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    park_size: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    region: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    management: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


# =====================================================
# 6. 환경 정보
# =====================================================

class TNoise(Base):
    __tablename__ = "t_noise"

    noise_max: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    noise_avg: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    noise_min: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True, primary_key=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class TJcgBjdTable(Base):
    __tablename__ = "t_jcg_bjd_table"

    region_name_full: Mapped[str] = mapped_column(
        Text, 
        primary_key=True,
        comment="전체 지역명"
    )
    ja_chi_gu_code: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    bjd_code: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("t_bjd_table.bjd_code", ondelete="CASCADE"),
        nullable=True,
        comment="법정동 코드"
    )

    # Relationships
    bjd: Mapped[Optional["TBjdTable"]] = relationship(back_populates="jcg_mappings")
