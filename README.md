# sli_direct_agent

# 프로젝트 clone

```
git clone https://github.com/persian815/sli_direct_agent.git
```

# 가상환경 구성

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# 패키지 수동설치

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
