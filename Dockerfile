FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치 (레이어 캐시 활용)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성만 먼저 복사 → requirements.txt 변경 없으면 캐시 재사용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# non-root 사용자 실행 (보안)
RUN useradd -m appuser
USER appuser

# GEMINI_API_KEY는 런타임에 환경변수로 주입 (빌드 시 포함 금지)
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
