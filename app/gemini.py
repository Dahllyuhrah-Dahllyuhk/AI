import os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ 환경 변수 GEMINI_API_KEY가 설정되지 않았습니다.")

genai.configure(api_key=API_KEY)

def generate_text(prompt: str, model: str = "gemini-2.5-flash") -> str:
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt)
    return response.text