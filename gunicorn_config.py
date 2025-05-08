import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 2
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 시작 시 디버깅 정보 출력
print(f"Gunicorn 바인딩: {bind}")
print(f"작업 디렉토리: {os.getcwd()}")
print(f"환경 변수 목록: {list(os.environ.keys())}")
print(f"PORT 환경 변수: {os.environ.get('PORT', '없음')}")