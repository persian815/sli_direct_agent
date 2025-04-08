# sli_direct_agent

# 가상환경 구성
```
cd myproject  # 프로젝트 폴더로 이동
python3 -m venv .venv
source .venv/bin/activate
```

# 패키지 설치
```
pip install streamlit langchain langchain-community langchain-core ollama boto3
```

# ollama 서버 실행
```
ollama serve

# 백그라운드 실행
nohup ollama serve > ollama.log 2>&1 &
```

## 스트리밋 실행
```
sh run.sh
```
