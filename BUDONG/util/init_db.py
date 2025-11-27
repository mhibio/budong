#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
스키마 생성 및 더미 데이터 삽입
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from BUDONG.api.core.database import engine, Base
from BUDONG.api.models import models  # noqa: F401 - 모델들을 import하여 등록


def init_database():
    """데이터베이스 초기화: 테이블 생성"""
    print("=" * 50)
    print("BUDONG 데이터베이스 초기화 시작")
    print("=" * 50)
    
    try:
        # 모든 테이블 생성
        print("\n📊 테이블 생성 중...")
        Base.metadata.create_all(bind=engine)
        print("✅ 테이블 생성 완료!")
        
        # 테이블 목록 확인
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"\n📋 생성된 테이블 ({len(tables)}개):")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        return False


def insert_dummy_data():
    """더미 데이터 삽입"""
    print("\n" + "=" * 50)
    print("더미 데이터 삽입 시작")
    print("=" * 50)
    
    try:
        from BUDONG.api.core.database import SessionLocal
        from BUDONG.api.models.models import (
            TUser, TBuilding, TRegion, TSchool,
            TRealTransactionPrice, TBuildingReview, TUserSavedBuilding,
            TSchoolDetail, TParkDetail, TRegionStats,
            TStation, TNoise
        )
        from sqlalchemy import func
        
        db = SessionLocal()
        
        # 1. 지역 데이터
        print("\n1️⃣ 지역 데이터 삽입 중...")
        regions = [
            {
                'bjd_code': '1168010100',
                'region_name_full': '서울특별시 강남구 역삼동',
                'region_polygon': 'POLYGON((127.028 37.500, 127.032 37.500, 127.032 37.504, 127.028 37.504, 127.028 37.500))'
            },
            {
                'bjd_code': '1168010200',
                'region_name_full': '서울특별시 강남구 개포동',
                'region_polygon': 'POLYGON((127.050 37.480, 127.055 37.480, 127.055 37.485, 127.050 37.485, 127.050 37.480))'
            },
            {
                'bjd_code': '1168010300',
                'region_name_full': '서울특별시 강남구 삼성동',
                'region_polygon': 'POLYGON((127.045 37.510, 127.050 37.510, 127.050 37.515, 127.045 37.515, 127.045 37.510))'
            }
        ]
        
        for region_data in regions:
            existing = db.query(TRegion).filter(TRegion.bjd_code == region_data['bjd_code']).first()
            if not existing:
                # SQL로 직접 삽입 (Spatial 타입 때문에)
                db.execute(text(
                    f"INSERT INTO t_region (bjd_code, region_name_full, region_polygon) "
                    f"VALUES (:bjd_code, :region_name_full, :polygon) "
                    f"ON DUPLICATE KEY UPDATE region_name_full = VALUES(region_name_full)"
                ), {
                    'bjd_code': region_data['bjd_code'],
                    'region_name_full': region_data['region_name_full'],
                    'polygon': region_data['region_polygon']
                })
        db.commit()
        print("✅ 지역 데이터 삽입 완료")
        
        # 2. 사용자 데이터
        print("\n2️⃣ 사용자 데이터 삽입 중...")
        users = [
            TUser(email='user1@example.com', password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5q5', nickname='홍길동'),
            TUser(email='user2@example.com', password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5q5', nickname='김철수'),
            TUser(email='user3@example.com', password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5q5', nickname='이영희'),
            TUser(email='admin@example.com', password_hash='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5q5', nickname='관리자')
        ]
        for user in users:
            existing = db.query(TUser).filter(TUser.email == user.email).first()
            if not existing:
                db.add(user)
        db.commit()
        print("✅ 사용자 데이터 삽입 완료")
        
        # 3. 건물 데이터 (SQL로 직접 삽입 - Spatial 타입)
        print("\n3️⃣ 건물 데이터 삽입 중...")
        buildings_sql = [
            ("1168010100", "서울특별시 강남구 역삼동 123-45", "래미안 역삼", "아파트", 2015, 500, "POINT(127.030 37.502)"),
            ("1168010100", "서울특별시 강남구 역삼동 234-56", "힐스테이트 역삼", "아파트", 2018, 300, "POINT(127.031 37.503)"),
            ("1168010200", "서울특별시 강남구 개포동 345-67", "개포래미안", "아파트", 2012, 400, "POINT(127.052 37.482)"),
            ("1168010300", "서울특별시 강남구 삼성동 456-78", "삼성동 오피스텔", "오피스텔", 2020, 200, "POINT(127.047 37.512)"),
            ("1168010100", "서울특별시 강남구 역삼동 567-89", "역삼동 빌라", "빌라", 2010, 20, "POINT(127.029 37.501)")
        ]
        
        for bjd_code, address, name, btype, year, units, point in buildings_sql:
            existing = db.execute(text(
                "SELECT building_id FROM t_building WHERE address = :address"
            ), {'address': address}).first()
            if not existing:
                db.execute(text(
                    "INSERT INTO t_building (bjd_code, address, building_name, building_type, build_year, total_units, location) "
                    "VALUES (:bjd_code, :address, :name, :type, :year, :units, :point)"
                ), {
                    'bjd_code': bjd_code,
                    'address': address,
                    'name': name,
                    'type': btype,
                    'year': year,
                    'units': units,
                    'point': point
                })
        db.commit()
        print("✅ 건물 데이터 삽입 완료")
        
        # 나머지 데이터는 SQL 파일을 직접 실행하는 방식으로 처리
        print("\n4️⃣ 나머지 더미 데이터는 init/02_init_data.sql 파일을 참고하세요.")
        print("   또는 MySQL 클라이언트로 직접 실행하세요:")
        print("   mysql -ubudonguser -pbudongpassword budong < init/02_init_data.sql")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 더미 데이터 삽입 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n" + "=" * 50)
        response = input("더미 데이터를 삽입하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            insert_dummy_data()
        else:
            print("\n💡 더미 데이터는 나중에 다음 명령으로 삽입할 수 있습니다:")
            print("   python3 BUDONG/util/init_db.py")
            print("   또는")
            print("   mysql -ubudonguser -pbudongpassword budong < init/02_init_data.sql")
    
    print("\n" + "=" * 50)
    print("✅ 데이터베이스 초기화 완료!")
    print("=" * 50)

