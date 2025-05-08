import os
import openai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 가져오기
api_key = os.environ.get('OPENAI_API_KEY')

print(f"API 키 존재 여부: {'있음' if api_key else '없음'}")
print(f"API 키 첫 4자리: {api_key[:4] if api_key and len(api_key) > 4 else '없음'}")

# API 키 설정
openai.api_key = api_key

# 테스트 호출
try:
    models = openai.Model.list()
    print("\n✅ API 연결 성공!")
    print("사용 가능한 모델 목록 (최대 5개):")
    for i, model in enumerate(models.data[:5]):
        print(f"- {model.id}")
except Exception as e:
    print("\n❌ API 연결 실패!")
    print(f"오류 메시지: {str(e)}") 