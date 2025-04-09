#!/bin/bash
source .venv/bin/activate

# 환경 변수 설정
# 기본값은 local로 설정
export ENV=${ENV:-local}

# 환경 변수가 server로 설정된 경우에만 서버 모드로 실행
if [ "$ENV" = "server" ]; then
    echo "Running in server mode (EC2)"
else
    echo "Running in local mode"
fi

streamlit run multi_app.py --server.port 8081

## streamlit run bedrock_app.py --server.port 8082
## streamlit run ollama_app.py --server.port 8083