#!/bin/bash

# 로깅 활성화
set -x

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# PYTHONPATH 설정 - 현재 디렉토리를 Python 경로에 추가
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Python 버전 확인
python --version

# Streamlit 버전 확인
streamlit --version

# 시작 명령 출력
echo "Starting Streamlit application..."

# Streamlit 애플리케이션 실행 (절대 경로 사용)
cd /home/site/wwwroot
streamlit run /home/site/wwwroot/src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 