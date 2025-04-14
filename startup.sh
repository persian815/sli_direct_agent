#!/bin/bash

# 로깅 활성화
set -x

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# pip 업그레이드
python -m pip install --upgrade pip

# 필요한 패키지 설치
echo "Installing required packages..."
pip install -r requirements.txt

# PYTHONPATH 설정
export PYTHONPATH=/home/site/wwwroot:/home/site/wwwroot/src:$PYTHONPATH

# Python 버전 확인
echo "Python version:"
python --version

# pip 목록 확인
echo "Installed packages:"
pip list

# Streamlit 버전 확인
echo "Streamlit version:"
streamlit --version

# 시작 명령 출력
echo "Starting Streamlit application..."

# Streamlit 애플리케이션 실행
streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 