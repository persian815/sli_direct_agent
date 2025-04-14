#!/bin/bash

# 로깅 활성화
set -x

# Azure 웹앱 이름과 리소스 그룹 설정
WEBAPP_NAME="slifit"
RESOURCE_GROUP="slihackathon-2025-team2-rg"

# 서버 중지
echo "Stopping Azure Web App..."
az webapp stop --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# /home/site/wwwroot 디렉토리로 이동
cd /home/site/wwwroot

# 디렉토리 내용 확인
echo "Contents of /home/site/wwwroot before extraction:"
ls -la

# output.tar.gz 파일이 있는지 확인하고 압축 해제
if [ -f "output.tar.gz" ]; then
    echo "Found output.tar.gz in /home/site/wwwroot, extracting..."
    
    # 파일 정보 확인
    echo "File information:"
    file output.tar.gz
    
    # 파일 크기 확인
    echo "File size:"
    ls -lh output.tar.gz
    
    # 압축 해제 시도 (자세한 로깅 포함)
    echo "Attempting to extract output.tar.gz..."
    tar -tvf output.tar.gz || echo "Failed to list contents of tar file"
    
    # 압축 해제 시도 1
    echo "Extraction attempt 1:"
    if tar -xzf output.tar.gz -v; then
        echo "Extraction successful. Directory contents after extraction:"
        ls -la
    else
        echo "First extraction attempt failed. Trying alternative method..."
        
        # 압축 해제 시도 2 (gzip과 tar 분리)
        echo "Extraction attempt 2 (using gzip and tar separately):"
        if gzip -dc output.tar.gz | tar xf - -v; then
            echo "Alternative extraction successful. Directory contents after extraction:"
            ls -la
        else
            echo "Second extraction attempt failed. Trying another method..."
            
            # 압축 해제 시도 3 (임시 디렉토리 사용)
            echo "Extraction attempt 3 (using temporary directory):"
            mkdir -p /tmp/extract
            if cp output.tar.gz /tmp/extract/ && cd /tmp/extract && tar -xzf output.tar.gz -v; then
                echo "Third extraction attempt successful. Copying files back..."
                cp -rv * /home/site/wwwroot/
                cd /home/site/wwwroot
                echo "Directory contents after copying back:"
                ls -la
            else
                echo "All extraction attempts failed."
            fi
        fi
    fi
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
if [ -d "antenv" ]; then
    source antenv/bin/activate
    echo "antenv virtual environment activated."
else
    echo "antenv directory not found. Creating a new virtual environment..."
    python -m venv antenv
    source antenv/bin/activate
    echo "New virtual environment created and activated."
fi

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

# 서버 재시작
echo "Restarting Azure Web App..."
az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

# 시작 명령 출력
echo "Starting Streamlit application..."

# Streamlit 애플리케이션 실행
streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 