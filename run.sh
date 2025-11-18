#!/bin/bash

# 프로젝트 실행 스크립트

echo "BUDONG 프로젝트 시작..."

# Docker Compose로 서비스 시작
docker-compose up -d

echo "서비스가 시작되었습니다."
echo "API 서버: http://localhost:8000"
echo "MySQL: localhost:3306"

