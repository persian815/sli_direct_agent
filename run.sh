#!/bin/bash
source .venv/bin/activate

# 환경 변수 설정
# 기본값은 local로 설정
export ENV=${ENV:-local}

# PYTHONPATH 설정 - 현재 디렉토리를 Python 경로에 추가
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 환경 변수가 server로 설정된 경우에만 서버 모드로 실행
if [ "$ENV" = "server" ]; then
    echo "Running in server mode (EC2)"
else
    echo "Running in local mode"
fi

#streamlit run src/app/components/main_chat2.py --server.port 8081
streamlit run src/app/main.py --server.port 8002 --server.enableCORS false




## streamlit run bedrock_app.py --server.port 8082
## streamlit run ollama_app.py --server.port 8083