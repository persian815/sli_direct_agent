#!/bin/bash
source .venv/bin/activate

# 환경 변수 설정
if [ "$(hostname)" = "ip-172-31-*" ]; then
    # EC2 환경
    export ENV=server
else
    # 로컬 환경
    export ENV=local
fi

streamlit run multi_app.py --server.port 8081

## streamlit run bedrock_app.py --server.port 8082
## streamlit run ollama_app.py --server.port 8083