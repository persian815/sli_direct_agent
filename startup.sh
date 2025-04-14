#!/bin/bash

# 로깅 활성화
set -x

# 현재 디렉토리 출력
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# /home/site/wwwroot 디렉토리 생성 (없는 경우)
mkdir -p /home/site/wwwroot

# 현재 디렉토리의 파일을 /home/site/wwwroot로 복사
echo "Copying files to /home/site/wwwroot..."
cp -rv * /home/site/wwwroot/

# /home/site/wwwroot 디렉토리로 이동
cd /home/site/wwwroot

# 복사된 파일 확인
echo "Files in /home/site/wwwroot:"
ls -la /home/site/wwwroot
echo "Files in /home/site/wwwroot/src:"
ls -la /home/site/wwwroot/src
echo "Files in /home/site/wwwroot/src/app:"
ls -la /home/site/wwwroot/src/app

# 가상 환경 생성
python -m venv antenv
source antenv/bin/activate

# 필요한 패키지 설치
pip install -r requirements.txt

# PYTHONPATH 설정 - 루트 디렉토리를 Python 경로에 추가
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Python 버전 확인
python --version

# Streamlit 버전 확인
streamlit --version

# 시작 명령 출력
echo "Starting Streamlit application..."

# Streamlit 애플리케이션 실행 (절대 경로 사용)
streamlit run /home/site/wwwroot/src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 