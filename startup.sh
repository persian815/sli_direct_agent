#!/bin/bash

# 로깅 활성화
set -x

# Azure 웹앱 이름과 리소스 그룹 설정
WEBAPP_NAME="slifit"
RESOURCE_GROUP="slihackathon-2025-team2-rg"

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Azure가 압축을 푼 디렉토리 찾기
echo "Searching for extracted deployment directory..."

# /tmp 디렉토리에서 최근에 생성된 디렉토리 찾기
LATEST_TMP_DIR=$(find /tmp -maxdepth 1 -type d -name "8dd7b4*" -o -name "zipdeploy" | sort -r | head -n 1)

if [ -n "$LATEST_TMP_DIR" ]; then
    echo "Found deployment directory: $LATEST_TMP_DIR"
    
    # 디렉토리 내용 확인
    echo "Contents of $LATEST_TMP_DIR:"
    ls -la "$LATEST_TMP_DIR"
    
    # 파일 복사
    echo "Copying files from $LATEST_TMP_DIR to /home/site/wwwroot..."
    if [ -d "$LATEST_TMP_DIR/extracted" ]; then
        cp -rv "$LATEST_TMP_DIR/extracted/"* /home/site/wwwroot/
    else
        cp -rv "$LATEST_TMP_DIR/"* /home/site/wwwroot/
    fi
    
    echo "Copy complete. Directory contents after copy:"
    ls -la /home/site/wwwroot
else
    echo "No deployment directory found in /tmp."
fi

# /home/site/wwwroot 디렉토리로 이동
cd /home/site/wwwroot

# startup.sh 파일이 있는지 확인하고 실행 권한 부여
if [ -f "startup.sh" ]; then
    echo "Found startup.sh, setting execute permissions..."
    chmod +x startup.sh
else
    echo "startup.sh not found in /home/site/wwwroot."
fi

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