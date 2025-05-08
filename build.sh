#!/usr/bin/env bash
# Render.com 빌드 스크립트

set -o errexit

echo "빌드 스크립트 시작..."
echo "Python 버전: $(python --version)"
echo "작업 디렉토리: $(pwd)"
echo "파일 목록:"
ls -la

# 의존성 설치
pip install -r requirements.txt

echo "PORT 환경 변수: $PORT"
echo "빌드 스크립트 완료" 