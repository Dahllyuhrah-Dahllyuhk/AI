from fastapi import FastAPI
from app.gemini import generate_text
from pydantic import BaseModel
import uvicorn

# cd C:\Users\HJ\Desktop\AI
# uvicorn app.main:app --reload

app = FastAPI(title="AI Server", version="1.0.0")

# 요청 모델 정의
class RequestBody(BaseModel):
    prompt: str

# 텍스트 생성 엔드포인트
@app.post("/generate")
def generate(request: RequestBody):
    try:
        result = generate_text(request.prompt, model="gemini-2.5-flash")
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 기본 루트 확인용
@app.get("/")
def root():
    return {"message": "서버 동작중!"}

# 로컬 실행 명령
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)
