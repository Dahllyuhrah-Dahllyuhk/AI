from fastapi import FastAPI, HTTPException
from app.gemini import generate_text
from pydantic import BaseModel
import uvicorn
import json
# cd C:\Users\HJ\Desktop\AI
# uvicorn app.main:app --reload

app = FastAPI(title="AI Server", version="1.0.0")

class RequestBody(BaseModel):
    prompt: str

# 카테고리 분류
def classify(request: RequestBody):
    try:
        prompt = (
            "다음 요청문을 일정생성/일정조회/일정삭제/일정수정/모임생성 중 하나로 분류하세요. "
            "해당하지 않으면 'null' 을 반환하세요.\n"
            f"요청문: {request.prompt}"
        )

        result = generate_text(prompt, model="gemini-2.5-flash")

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)