from fastapi import FastAPI, HTTPException
from app.gemini import generate_text
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pydantic import BaseModel
from pydantic import BaseModel
from typing import Any, Optional
import uvicorn
import json
# cd C:\Users\HJ\Desktop\AI
# uvicorn app.main:app --reload --host 0.0.0.0 --port 5000


app = FastAPI(title="AI Server", version="1.0.0")

class RequestBody(BaseModel):
    prompt: str

# Main server 요청시 이곳으로 오게 됨
@app.post("/main")
def main(request: RequestBody):
    input = request.prompt

    # 질의 카테고리 분류 -> 라우팅 -> 해당 메소드 활용 -> 스프링부트 파싱 후 반환
    category = classify(input)
    data = routing(category, input)

    return parsing(category, data)

# 메인서버 리턴용 파싱 메소드
def parsing(category: str, data):
    return {
        "category": category,
        "data": data
    }

def routing(category, text:str): 
    if(category == "일정생성"): 
        print("일정생성")
        return generate_schedule(text) 
    elif(category == "일정조회"): 
        print("일정조회")
        return search_schedule(text)
    elif(category == "일정삭제"): 
        print("일정삭제")
        return search_schedule(text)
    elif(category == "모임생성"): 
        print("모임생성")
        return generate_meeting(text)
    elif(category == "모임조회"): 
        print("모임조회")
        return get_meeting(text)
    

#모임 조회
def get_meeting(text:str):
    # 1. 날짜 계산을 위한 기준 시간 설정 (KST)
    try:
        kst = ZoneInfo("Asia/Seoul")
    except:
        from datetime import timezone, timedelta
        kst = timezone(timedelta(hours=9))

    now = datetime.now(kst)
    current_date_str = now.strftime("%Y-%m-%d %H:%M:%S (%A)") # 예: 2025-11-26 (Wednesday)

    try:
        prompt = (
            f"기준 시각(Today): {current_date_str}\n"
            "사용자의 요청에서 검색 조건인 '모임 제목(title)'과 '날짜 범위(Start/End)'를 JSON으로 추출하세요.\n"
            "응답은 반드시 JSON만 포함하세요. (코드블록 ``` 금지)\n\n"

            "⭐⭐[추출 규칙]⭐⭐\n"
            "1. **title**: 검색할 키워드. (없으면 \"\")\n"
            "2. **dateRangeStart**, **dateRangeEnd**:\n"
            "   - 형식: 'YYYY-MM-DD'\n"
            "   - 날짜 언급이 없으면 둘 다 null로 설정.\n"
            "   - '내일' -> 내일 날짜로 Start, End 동일하게 설정.\n"
            "   - '다음 주' -> 다음 주 월요일 ~ 일요일 범위로 설정.\n"
            "   - '11월 모임' -> 11월 1일 ~ 11월 30일 범위로 설정.\n\n"

            "⭐⭐[예시]⭐⭐\n"
            "Q: '다음 주 회식 모임 있어?'\n"
            "A: {\"title\": \"회식\", \"dateRangeStart\": \"2025-12-01\", \"dateRangeEnd\": \"2025-12-07\"}\n\n"
            
            "Q: '크리스마스 모임 정보 알려줘'\n"
            "A: {\"title\": \"크리스마스\", \"dateRangeStart\": \"2025-12-25\", \"dateRangeEnd\": \"2025-12-25\"}\n\n"
            
            "Q: '잡혀있는 모임 다 보여줘' (날짜/제목 없음)\n"
            "A: {\"title\": \"\", \"dateRangeStart\": null, \"dateRangeEnd\": null}\n\n"

            f"요청문: {text}"
        )

        # 모델 호출
        result = generate_text(prompt, model="gemini-2.5-flash")

        # 결과 정제
        cleaned = (
            result.replace("```json", "")
                  .replace("```", "")
                  .strip()
        )

        data = json.loads(cleaned)
        print(data)
        
        # 반환 데이터 구성
        return {
            "title": data.get("title", ""),
            "dateRangeStart": data.get("dateRangeStart"), # null 가능
            "dateRangeEnd": data.get("dateRangeEnd")      # null 가능
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON 파싱 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 모임 생성
def generate_meeting(text: str):
    try:
        kst = ZoneInfo("Asia/Seoul")
    except:
        from datetime import timezone, timedelta
        kst = timezone(timedelta(hours=9))

    now = datetime.now(kst)
    current_full_str = now.strftime("%Y-%m-%d %H:%M:%S (%A)")
    
    # 요일 계산을 돕기 위해 현재 요일 명시
    weekday_kor = ["월", "화", "수", "목", "금", "토", "일"]
    current_day_kor = weekday_kor[now.weekday()]

    try:
        prompt = (
            f"기준 시각(Today): {current_full_str}\n"
            f"오늘은 '{current_day_kor}요일'입니다.\n\n"

            "사용자의 요청에서 '모임 생성'을 위한 정보를 추출하여 JSON으로 반환하세요.\n"
            "모임은 보통 특정 날짜 하루일 수도 있고, '다음 주', '주말' 처럼 기간일 수도 있습니다.\n\n"

            "⭐⭐[필드별 작성 규칙]⭐⭐\n"
            "1. **title**: 모임 제목 (없으면 '모임'으로 설정)\n"
            "2. **dateRangeStart**, **dateRangeEnd**: \n"
            "   - 형식: 'YYYY-MM-DD' (시간 제외)\n"
            "   - '다음 주'라고 하면: 다음 주 월요일 ~ 일요일 날짜로 계산.\n"
            "   - '내일'이라고 하면: Start와 End를 내일 날짜로 동일하게 설정.\n"
            "3. **isAllDay**:\n"
            "   - 특정 시간(예: 2시, 저녁 등) 언급이 없으면 -> true\n"
            "   - 시간 언급이 있으면 -> false\n"
            "4. **timeConstraints** (List):\n"
            "   - isAllDay가 true면 -> [] (빈 리스트)\n"
            "   - isAllDay가 false면 -> [{'start': 'HH:mm', 'end': 'HH:mm'}] 형식으로 작성.\n"
            "   - 예: '2시부터 4시' -> start: '14:00', end: '16:00'\n"
            "   - 예: '오후 2시' (종료 없음) -> start: '14:00', end: '15:00' (기본 1시간)\n\n"

            "⭐⭐[예시]⭐⭐\n"
            "Q: '다음 주 회식 모임 잡아줘'\n"
            "A: {\"title\": \"회식\", \"dateRangeStart\": \"2025-12-01\", \"dateRangeEnd\": \"2025-12-07\", \"isAllDay\": true, \"timeConstraints\": []}\n\n"
            
            "Q: '이번 주 금요일 7시부터 21시 사이에 저녁 모임'\n"
            "A: {\"title\": \"저녁 모임\", \"dateRangeStart\": \"2025-11-28\", \"dateRangeEnd\": \"2025-11-28\", \"isAllDay\": false, \"timeConstraints\": [{\"start\": \"07:00\", \"end\": \"21:00\"}]}\n\n"

            f"요청문: {text}"
        )

        # 모델 호출 (Gemini 등 사용)
        result = generate_text(prompt, model="gemini-2.5-flash")

        # JSON 정제
        cleaned = (
            result.replace("```json", "")
                  .replace("```", "")
                  .strip()
        )
        
        meeting_data = json.loads(cleaned)
        print(meeting_data)

        return meeting_data

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON 파싱 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 일정 생성
def generate_schedule(text: str):
    # 1. 한국 시간(KST) 및 기준 정보 확보
    try:
        kst = ZoneInfo("Asia/Seoul")
    except:
        from datetime import timezone, timedelta
        kst = timezone(timedelta(hours=9))

    now = datetime.now(kst)
    current_full_str = now.strftime("%Y-%m-%d %H:%M:%S (%A)") # 2025-11-24 ...
    current_year = now.year
    
    try:
        # 2. 강력한 우선순위 규칙을 적용한 프롬프트
        prompt = (
            f"기준 시각(Today): {current_full_str}\n"
            "사용자의 입력을 분석하여 일정 JSON을 생성하세요.\n\n"

            "⭐⭐[최우선 순위 규칙 - 절대 준수]⭐⭐\n"
            "1. **직접 언급된 날짜가 1순위입니다.**\n"
            "   - 사용자가 '11월 28일'이라고 하면, 무조건 '11월 28일'로 설정하세요. (오늘 날짜 무시)\n"
            "   - 사용자가 '28일'이라고 하면, 이번 달(또는 가까운 미래)의 '28일'로 설정하세요.\n"
            "2. **연도(Year) 보정**:\n"
            "   - 날짜에 연도가 없으면 '기준 시각'의 연도({current_year})를 사용하세요.\n"
            "   - 단, 요청한 월이 이미 지났다면 내년({current_year + 1})으로 설정하세요.\n"
            "3. **시간 처리**:\n"
            "   - 시간 언급이 없으면 -> \"allDay\": true, \"00:00:00\" ~ \"23:59:59\"\n"
            "   - '오후 3시' 등 언급이 있으면 -> 해당 시간으로 설정 (allDay: false)\n\n"

            "⭐⭐[입력 패턴별 예시]⭐⭐\n"
            "Q: \"11월 28일 회식\" (기준이 11월 24일일 때)\n"
            "A: {\"title\": \"회식\", \"start\": \"2025-11-28T00:00:00+09:00\", \"end\": \"2025-11-28T23:59:59+09:00\", \"allDay\": true}\n\n"
            
            "Q: \"내년 1월 5일 미팅\"\n"
            "A: {\"title\": \"미팅\", \"start\": \"2026-01-05T00:00:00+09:00\", \"end\": \"2026-01-05T23:59:59+09:00\", \"allDay\": true}\n\n"

            f"요청문: {text}"
        )

        # 모델 호출
        result = generate_text(prompt, model="gemini-2.5-flash")

        # 결과 정제
        cleaned = (
            result.replace("```json", "")
                  .replace("```", "")
                  .strip()
        )

        print(json.loads(cleaned))

        return json.loads(cleaned)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON 파싱 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#일정조회    
def search_schedule(text: str):
    # 1. LLM에게 현재 기준 시간을 알려줘야 "내일", "다음 주" 등을 계산할 수 있습니다.
    now = datetime.now()
    current_context = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # 2. 프롬프트 작성
        prompt = (
            f"현재 시각: {current_context}\n"
            "다음 요청문에서 일정 조회(검색) 조건을 JSON 형식으로 추출하세요.\n"
            "응답은 반드시 JSON만 포함하고, 코드블록(```)을 사용하지 마세요.\n\n"
            "규칙:\n"
            "1. 'keyword': 검색어가 있다면 추출 (없으면 null)\n"
            "2. 'start', 'end': 조회 기간을 ISO 8601 형식(YYYY-MM-DDTHH:mm:ss)으로 변환. (기간 언급이 없으면 null)\n"
            "3. 'start'와 'end'는 쿼리문이 의미하는 전체 범위를 포괄해야 함.\n\n"
            "예시 1 (검색어만): '회식 일정 찾아줘' -> {\"keyword\": \"회식\", \"start\": null, \"end\": null}\n"
            "예시 2 (기간만): '다음 주 일정 보여줘' -> {\"keyword\": null, \"start\": \"2025-11-24T00:00:00\", \"end\": \"2025-11-30T23:59:59\"}\n"
            "예시 3 (둘 다): '내일 미팅 일정 있어?' -> {\"keyword\": \"미팅\", \"start\": \"2025-11-19T00:00:00\", \"end\": \"2025-11-19T23:59:59\"}\n\n"
            f"요청문: {text}"
        )

        # 3. 모델 호출 (generate_text 함수는 이미 있다고 가정)
        result = generate_text(prompt, model="gemini-2.5-flash")

        # 4. 결과 정제 (백틱 제거)
        cleaned = (
            result.replace("```json", "")
                  .replace("```", "")
                  .strip()
        )

        # 5. JSON 파싱
        search_data = json.loads(cleaned)

        # 6. [중요] Java DTO 호환을 위해 ISO 문자열 -> Long(Timestamp) 변환
        # Java의 SelectSchedule { Long start; Long end; ... } 와 매칭
        final_data = {
            "keyword": search_data.get("keyword"),
            "start": to_timestamp_millis(search_data.get("start")),
            "end": to_timestamp_millis(search_data.get("end"))
        }

        
        print(final_data)

        return final_data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="JSON 형식 파싱 실패. 모델이 잘못된 형식을 반환했습니다."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 카테고리 분류
def classify(text:str):
    try:
        prompt = (
            "다음 요청문을 일정생성/일정조회/일정삭제/모임조회/모임생성 중 하나로 분류하세요. "
            "해당하지 않으면 'null' 을 반환하세요.\n"
            f"요청문: {text}"
        )

        result = generate_text(prompt, model="gemini-2.5-flash")

        return result.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class SummaryRequest(BaseModel):
    category: str
    data: Any 

    
@app.post("/summary")
def generate_summary_api(req: SummaryRequest):
    try:
        prompt = (
            "너는 사용자의 일정 관리 비서야. 아래 '결과 데이터'를 분석해서 사용자에게 **가장 필요한 정보를 요약(Briefing)**해줘.\n\n"
            
            f"카테고리: {req.category}\n"
            f"데이터: {json.dumps(req.data, ensure_ascii=False, default=str)}\n\n"

            "⭐⭐[상황별 브리핑 가이드]⭐⭐\n"
            "1. **모임조회 (가장 중요)**:\n"
            "   - 데이터가 리스트라면 '총 N개의 모임이 있습니다'로 시작.\n"
            "   - **확정된 모임(CONFIRMED)**: '[모임명]은 [날짜] [시간]에 확정되었어요. 늦지 않게 준비하세요!'\n"
            "   - **조율 중(PENDING)**: '[모임명]은 아직 조율 중이에요. 참여자 N명 중 M명이 응답했어요.'\n"
            "   - **종료됨(CLOSED)**: '[모임명]은 종료된 모임입니다.'\n"
            "   - 참여자 이름이 있다면 '누구누구님이 아직 응답하지 않았어요' 처럼 팁을 줘도 좋아.\n"
            
            "2. **일정조회**:\n"
            "   - '요청하신 날짜에 [일정제목] 등 총 N건의 일정이 있어요.'\n"
            
            "3. **생성/삭제**:\n"
            "   - 깔끔하게 완료 사실만 전달. (예: '소고기 파티 일정을 등록했습니다.')\n\n"
            
            "⭐⭐[말투]⭐⭐\n"
            "- 친절하고 전문적인 비서 톤 (해요체).\n"
            "- 너무 길지 않게 1~2문장으로 핵심만 전달.\n"
            "- 응답은 오직 **텍스트(String)**만 반환."
        )

        summary_text = generate_text(prompt, model="gemini-2.5-flash")
        return {"summary": summary_text.strip().strip('"')}

    except Exception as e:
        print(f"Error: {e}")
        return {"summary": "요청하신 정보는 다음과 같아요."}

def to_timestamp_millis(iso_str):
    if not iso_str:
        return None
    try:
        # ISO 형식이 '2025-11-15T09:00:00' 형태라고 가정
        dt = datetime.fromisoformat(iso_str)
        # 1초 = 1000밀리초
        return int(dt.timestamp() * 1000)
    except ValueError:
        return None
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=False)