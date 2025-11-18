from contextlib import asynccontextmanager
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from BUDONG.api.routers.v1 import api
from BUDONG.config import settings
from BUDONG.api.core.database import check_and_create_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 이벤트"""
    # 시작 시 - 데이터베이스 스키마 자동 검사 및 생성
    logger.info("=" * 50)
    logger.info("BUDONG API 서버 시작 중...")
    logger.info("=" * 50)
    
    # 데이터베이스 연결 대기 (최대 30초)
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if check_and_create_tables():
                logger.info("✅ 데이터베이스 스키마 검사 및 생성 완료")
                break
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"데이터베이스 연결 대기 중... ({retry_count}/{max_retries})")
                time.sleep(1)
            else:
                logger.error(f"❌ 데이터베이스 연결 실패: {e}")
                logger.warning("⚠️ 데이터베이스 연결 없이 서버를 시작합니다.")
    
    logger.info("=" * 50)
    
    yield
    
    # 종료 시 (필요시 정리 작업)
    logger.info("BUDONG API 서버 종료 중...")


app = FastAPI(
    title="BUDONG API",
    description="BUDONG Database Project API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {"message": "BUDONG API Server", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

