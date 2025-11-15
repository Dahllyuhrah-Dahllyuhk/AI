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

# 일정 생성
def generate_schedule(request: RequestBody):
    text = request.prompt
    try:
        prompt = (
            "다음 요청문에서 일정 생성 정보를 JSON 형식으로 추출하세요.\n"
            "응답은 반드시 JSON만 포함하도록 하세요. 코드블록(```)을 사용하지 마세요.\n"
            "예시: {\"title\": \"회의\", \"description\": \"상담 회의\", \"start\": \"2025-11-15T09:00:00+09:00\", \"end\": \"2025-11-15T11:00:00+09:00\", \"allDay\": false, \"timeZone\": \"Asia/Seoul\"}\n"
            f"요청문: {text}"
        )

        # generate_text는 문자열을 반환한다고 가정
        result = generate_text(prompt, model="gemini-2.5-flash")

        # result는 문자열이므로 백틱 제거
        cleaned = (
            result.replace("```json", "")
                  .replace("```", "")
                  .strip()
        )

        # JSON 파싱
        schedule_data = json.loads(cleaned)

        return {"result": schedule_data}

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="JSON 형식 파싱 실패. 모델이 잘못된 형식을 반환했습니다."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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