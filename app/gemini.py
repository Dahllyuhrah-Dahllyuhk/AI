import os
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수에서 API 키 읽기 (또는 직접 입력)
API_KEY = os.getenv("GEMINI_API_KEY", "여기에_키_삽입")

# 클라이언트 초기화
genai.configure(api_key=API_KEY)

def generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt)
    return response.text
