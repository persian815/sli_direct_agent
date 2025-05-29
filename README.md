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

## 릴리즈 노트 250410

```
- 채팅 인터페이스 개선
  - 질문과 답변을 말풍선 형태로 변경 (질문은 왼쪽, 답변은 오른쪽)
  - 답변 속도 조절로 더 자연스러운 대화 느낌 제공
  - 채팅 아이콘 크기 조정 (정사각형 유지)
- 지식 수준 평가 시스템 개선
  - 지식 수준 점수 범위를 1-10에서 1-100으로 확장
  - 지식 수준 분포 그래프 개선 (10단위 범위로 그룹화)
  - 지식 수준 표시 바 개선
- UI/UX 개선
  - 텍스트 정렬 문제 해결 (왼쪽 정렬로 통일)
  - 메시지 영역 너비 확장으로 가독성 향상
  - 채팅 메시지 컨테이너 레이아웃 개선
```

## 릴리즈 노트 250414

```
MS Azure 연동
```

## 릴리즈 노트 250415

```₩₩₩₩
배포 수정 중
도서 베포
```

## 릴리즈 노트 250416

```₩₩₩₩
환경설정
```

## 릴리즈 노트 250422

```₩₩₩₩
시작
```

## 릴리즈 노트 250523

```UT 준비
시작
```
수정