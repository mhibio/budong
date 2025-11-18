from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from BUDONG.config import settings
import logging

logger = logging.getLogger(__name__)

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # SQL 쿼리 로깅 (개발 시 True로 변경 가능)
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 (모든 모델이 상속받을 클래스)
Base = declarative_base()


# 의존성 주입을 위한 DB 세션 생성기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection():
    """데이터베이스 연결 확인"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return False


def table_exists(table_name: str) -> bool:
    """특정 테이블이 존재하는지 확인"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"테이블 존재 확인 실패: {e}")
        return False


def check_and_create_tables():
    """스키마를 검사하고 필요한 테이블만 생성"""
    from BUDONG.api.models import models  # noqa: F401 - 모델들을 import하여 등록
    
    # 데이터베이스 연결 확인
    if not check_database_connection():
        logger.error("데이터베이스에 연결할 수 없습니다.")
        return False
    
    try:
        # 모든 모델의 테이블 목록 가져오기
        all_tables = list(Base.metadata.tables.keys())
        
        if not all_tables:
            logger.warning("생성할 테이블이 없습니다.")
            return False
        
        # 존재하지 않는 테이블 찾기
        missing_tables = []
        existing_tables = []
        
        for table_name in all_tables:
            if table_exists(table_name):
                existing_tables.append(table_name)
            else:
                missing_tables.append(table_name)
        
        # 결과 출력
        if existing_tables:
            logger.info(f"✅ 기존 테이블 ({len(existing_tables)}개): {', '.join(existing_tables)}")
        
        if missing_tables:
            logger.info(f"📊 생성할 테이블 ({len(missing_tables)}개): {', '.join(missing_tables)}")
            # 존재하지 않는 테이블만 생성
            Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables[table] for table in missing_tables])
            logger.info(f"✅ {len(missing_tables)}개의 테이블이 생성되었습니다.")
        else:
            logger.info("✅ 모든 테이블이 이미 존재합니다.")
        
        return True
        
    except Exception as e:
        logger.error(f"테이블 생성 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


# 데이터베이스 테이블 생성 함수 (개발용 - 모든 테이블 강제 생성)
def create_tables():
    """모든 테이블 생성 (기존 테이블 무시)"""
    from BUDONG.api.models import models  # noqa: F401 - 모델들을 import하여 등록
    Base.metadata.create_all(bind=engine)


# 데이터베이스 테이블 삭제 함수 (개발용)
def drop_tables():
    """모든 테이블 삭제 (주의: 데이터 손실)"""
    from BUDONG.api.models import models  # noqa: F401
    Base.metadata.drop_all(bind=engine)
