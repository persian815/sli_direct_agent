#!/bin/bash

# 로깅 활성화
set -x

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# /home/site/wwwroot 디렉토리로 이동
cd /home/site/wwwroot

# output.tar.gz 파일이 있는지 확인하고 압축 해제
if [ -f "output.tar.gz" ]; then
    echo "Found output.tar.gz in /home/site/wwwroot, extracting..."
    tar -xzf output.tar.gz -v
    echo "Extraction complete. Directory contents after extraction:"
    ls -la
else
    echo "output.tar.gz file not found in /home/site/wwwroot."
    
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

# antenv 가상 환경 활성화
echo "Activating antenv virtual environment..."
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

# 시작 명령 출력
echo "Starting Streamlit application..."

# Streamlit 애플리케이션 실행
streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 