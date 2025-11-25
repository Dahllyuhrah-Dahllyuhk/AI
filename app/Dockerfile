# 베이스 이미지 선택
FROM python:3.12-slim

# 1. [최적화] 로그가 버퍼링 없이 즉시 찍히도록 설정 (디버깅 용이)
ENV PYTHONUNBUFFERED=1

# 2. [최적화] 컨테이너 타임존을 한국(KST)으로 설정 
# (이전에 겪은 날짜 문제를 OS 차원에서 한 번 더 방지합니다)
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 작업 디렉토리 생성
WORKDIR /app

# 필요한 패키지 사전 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. [최적화] requirements.txt를 먼저 복사해서 설치
# (소스코드가 바뀌어도 라이브러리 설치 단계는 캐시를 사용하여 빌드 속도가 엄청 빨라짐)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스코드 복사
COPY . .

# uvicorn 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]