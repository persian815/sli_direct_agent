#!/bin/bash

# 로깅 활성화
set -x

# Azure 웹앱 이름과 리소스 그룹 설정
WEBAPP_NAME="slifit"
RESOURCE_GROUP="slihackathon-2025-team2-rg"

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# /tmp/8dd7b4cf3e60ee3 디렉토리 확인 (Azure가 압축을 푼 위치)
if [ -d "/tmp/8dd7b4cf3e60ee3" ]; then
    echo "Found /tmp/8dd7b4cf3e60ee3 directory, copying files..."
    cp -rv /tmp/8dd7b4cf3e60ee3/* /home/site/wwwroot/
    echo "Copy complete. Directory contents after copy:"
    ls -la
else
    echo "/tmp/8dd7b4cf3e60ee3 directory not found."
    
    # /tmp/zipdeploy/extracted 디렉토리 확인
    if [ -d "/tmp/zipdeploy/extracted" ]; then
        echo "Found /tmp/zipdeploy/extracted directory, copying files..."
        cp -rv /tmp/zipdeploy/extracted/* /home/site/wwwroot/
        echo "Copy complete. Directory contents after copy:"
        ls -la
    else
        echo "/tmp/zipdeploy/extracted directory not found."
    fi
fi

# /home/site/wwwroot 디렉토리로 이동
cd /home/site/wwwroot

# Python 가상 환경 설정
echo "Setting up Python environment..."
python -m venv antenv
source antenv/bin/activate

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

# Streamlit 애플리케이션 실행
echo "Starting Streamlit application..."
streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 