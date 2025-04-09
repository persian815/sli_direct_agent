# SLI Direct Agent

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
## 릴리즈 노트 250408
```
최초 생성 
```

## 릴리즈 노트 250409
```
- 프로젝트 구조 개선
  - 소스 코드를 역할별로 분리하여 디렉토리 구조화
    - `src/app/`: 메인 애플리케이션 코드
    - `src/llm/`: LLM 관련 함수들
    - `src/utils/`: 유틸리티 함수들 (dev_mode.py)
    - `src/visualization/`: 시각화 관련 함수들
  - 정적 파일 분리
    - `static/css/`: 스타일시트
    - `static/js/`: 자바스크립트 파일
  - `data/`: 데이터 파일 디렉토리 추가
- 코드 모듈화 및 개선
  - CSS 스타일을 별도 파일로 분리
  - 시각화 관련 코드를 별도 모듈로 분리
  - LLM 관련 함수들을 별도 모듈로 분리
  - 메인 애플리케이션 코드 정리
- 기능 개선
  - 사이드바 토글 시 채팅 입력창 위치 자동 조정
  - 사용자 지식 수준 평가 및 시각화 기능 추가
  - 채팅 인터페이스 UX/UI 개선
    - 입력창 포커스 효과 개선
    - 다크 모드 대비 개선
    - 채팅 입력창 고정 위치 설정
```