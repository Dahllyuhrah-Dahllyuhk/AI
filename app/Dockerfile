# 베이스 이미지 선택
FROM python:3.12-slim

# --- 추가된 부분 ---
ARG GEMINI_API_KEY
ENV GEMINI_API_KEY=$GEMINI_API_KEY
# -------------------

# 작업 디렉토리 생성
WORKDIR /app

# 필요한 패키지 사전 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 로컬 파일을 컨테이너로 복사
COPY . /app

# 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# uvicorn을 통한 FastAPI 실행 (포트 5000)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
