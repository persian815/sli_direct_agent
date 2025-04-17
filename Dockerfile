FROM python:3.9-slim

# 기본 도구 설치 + Azure CLI 설치
RUN apt-get update && apt-get install -y curl gnupg2 apt-transport-https ca-certificates lsb-release sudo \
  && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
  && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" \
     > /etc/apt/sources.list.d/azure-cli.list \
  && apt-get update && apt-get install -y azure-cli \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Azure CLI 설정 + ML 확장 설치
RUN az config set extension.use_dynamic_install=yes_without_prompt && \
    az config set extension.dynamic_install_allow_preview=true && \
    pip install --upgrade pip setuptools && \
    az extension add --name ml

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 먼저 복사 및 설치
COPY requirements.txt .
# requirements.txt 파일 존재 여부 확인
RUN if [ ! -f requirements.txt ]; then \
    echo "ERROR: requirements.txt file not found!" && exit 1; \
    fi && \
    echo "Installing dependencies from requirements.txt..." && \
    pip install --no-cache-dir -r requirements.txt || { \
    echo "ERROR: Failed to install dependencies from requirements.txt"; \
    exit 1; \
    }

# 애플리케이션 소스 복사
COPY . .

# 앱 실행 사용자 지정
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 환경변수 설정
ENV PYTHONPATH=/app:/app/src:/app
ENV PORT=8000

# 포트 노출
EXPOSE 8000

# 앱 실행
CMD ["python", "-m", "streamlit", "run", "src/app/main.py", "--server.port=8000", "--server.enableCORS=false", "--server.address=0.0.0.0"]