from flask import Flask, render_template, request, jsonify
import os
import csv
import difflib
import openai
import sys
from dotenv import load_dotenv

# 디버깅 정보 출력
print(f"Python 버전: {sys.version}")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"환경 변수 목록: {list(os.environ.keys())}")
print(f"PORT 환경 변수: {os.environ.get('PORT', '없음')}")

# .env 파일에서 환경 변수 로드 (로컬 개발용)
load_dotenv()

app = Flask(__name__)

# Render.com에서 포트 번호 처리를 명시적으로 설정
port = int(os.environ.get("PORT", 8080))
print(f"사용 포트: {port}")

# OpenAI API 키 설정
# 로컬에서는 .env 파일에서, 배포 환경에서는 환경 변수에서 직접 가져옴
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print("경고: OPENAI_API_KEY가 설정되지 않았습니다!")
openai.api_key = api_key

# 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, '견체공학_챗봇_보강본.csv')

# CSV 데이터 로드
data = []
try:
    with open(DATA_FILE, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            examples = [line.strip() for line in row['사용자 질문 예시'].splitlines() if line.strip()]
            row['examples'] = examples
            data.append(row)
    print(f"성공적으로 {len(data)}개의 데이터 로드됨")
except Exception as e:
    print(f"CSV 파일 로드 오류: {str(e)}")
    data = []

# 정적 응답 데이터
extra_data = {
    '강아지 정보 톡톡': '강아지에 대한 유익한 정보와 팁을 알려드릴게요!\n\n- 건강 관리: 정기적인 건강검진과 예방접종은 반려견 건강 유지의 기본입니다. 매일 적당한 운동과 균형 잡힌 식사를 제공하세요.\n\n- 훈련 팁: 일관된 명령어와 긍정적 강화를 통해 훈련하는 것이 효과적입니다. 짧고 자주 하는 훈련 세션이 집중력 유지에 도움이 됩니다.\n\n- 영양 정보: 강아지의 나이, 크기, 활동량에 맞는 사료 선택이 중요합니다. 과자나 간식은 전체 식사량의 10%를 넘지 않도록 주의하세요.\n\n더 도움이 필요하면 상담원 연결을 요청해주세요.',
    '견체공학 소개': '견체공학은 반려견과 보호자의 편안함을 최우선으로 생각하는 프리미엄 반려동물 용품 브랜드입니다.\n\n저희 브랜드는 수년간의 연구와 개발을 통해 반려견의 신체 구조와 행동 패턴을 과학적으로 분석하여 최적의 제품을 디자인합니다. 특히 \'어부바가방\'은 중형견 가방 시장에서 9년 연속 1위를 차지한 대표 제품으로, 반려견의 체형에 맞춘 인체공학적 설계가 특징입니다.\n\n또한 \'견글라스\'는 자외선으로부터 반려견의 눈을 보호하는 전문 선글라스로, 다양한 사이즈와 뛰어난 내구성을 자랑합니다.\n\n견체공학은 단순한 제품 판매를 넘어 반려견과 보호자의 더 행복한 일상을 만들어가는 동반자가 되고자 합니다.\n\n더 도움이 필요하면 상담원 연결을 요청해주세요.'
}

# 기본 카테고리 및 후속 옵션
CATEGORIES = ['어부바가방', '견글라스', '강아지 정보 톡톡', '견체공학 소개']
POST_OPTIONS = CATEGORIES + ['상담원 연결하기']

# 견체공학 브랜드 컨텍스트 및 응답 지침
BRAND_CONTEXT = """
견체공학은 반려견과 보호자의 편안함을 최우선으로 생각하는 브랜드입니다.
주요 제품:
1. 어부바가방 - 중형견 가방 시장에서 9년 연속 1위, 반려견을 편안하게 이동시켜주는 제품
2. 견글라스 - 강아지용 선글라스, 자외선으로부터 반려견의 눈을 보호

어부바3는 프리미엄형 어부바가방으로, 탈부착형 허리벨트와 허리보호커버가 있으며 토이론 3중 구조로 설계되었습니다.
어부바라이트2는 알뜰형 어부바가방으로, 소형견에게 적합하며 스냅 단추로 페일-세이프티를 구현했습니다.

견글라스는 강아지 머리 둘레에 따라 S(20~29cm), M(30~38cm), L(39~46cm) 사이즈로 구분되며,
토탈 케어 서비스를 통해 프레임 교체, 렌즈 교체, 부품 무상 수리 등을 제공합니다.
"""

RESPONSE_GUIDELINES = """
# 견체공학 질문 응답 지침

## 1. 기본 원칙
- 정확성: 실제 견체공학(브랜드, 제품, 서비스) 관련 공식 자료를 기반으로 답변합니다.
- 성실성: 질문을 대충 넘기지 않고, 질문 의도를 파악하여 구체적이고 도움되는 답변을 제공합니다.
- 브랜드 일관성: 견체공학의 브랜드 어조와 가치관(신뢰, 전문성, 따뜻함)에 맞는 말투를 유지합니다.
- 모를 경우: "정확한 답변을 위해 확인이 필요합니다."라고 정중히 안내하고, 추가 자료 요청이나 담당자 연결 제안을 합니다.

## 2. 답변 프로세스
질문 수신 → 의도 파악 → 자료 탐색 → 답변 작성 → 브랜드 톤 검토 → 최종 전달

## 3. 브랜드 어조 가이드
- 따뜻하고 신뢰감 있게: 고객의 질문을 소중하게 여긴다는 느낌을 전달
- 전문성을 갖춘 말투: 애매한 표현 없이 정확한 용어 사용
- 배려 있는 답변: 상대방 입장에서 이해하기 쉽게 설명

## 4. 답변 범위
- 제품 기능 질문: 제품 스펙, 기술 특징, 사용 방법을 설명
- 서비스 문의: 구매, A/S, 반품, 배송 정책 등 상세 안내
- 문제 해결 요청: 단계별 해결 가이드 제공 + 추가 문의 창구 안내
- 브랜드 철학 질문: 견체공학이 지향하는 가치와 비전, 설립 배경 등을 소개

## 5. 금지사항 (절대 금지)
- 추측하거나 부정확한 정보를 말하지 않는다.
- "잘 모릅니다", "모르겠어요"로만 답변하지 않는다.
- 고객을 무시하거나 불성실하게 대하는 어투를 사용하지 않는다.
- 브랜드 이미지와 맞지 않는 사적인 의견을 넣지 않는다.

## 6. 추가 지침
- 질문이 중복되더라도 매번 정성스럽게 답변한다.
- 대답만 하지 말고, 고객의 다음 궁금증을 예측해 추가 정보를 자연스럽게 제안한다.
- 답변 끝에는 "더 도움이 필요하면 상담원 연결을 요청해주세요." 문구를 추가한다.
"""

@app.route('/')
def index():
    print(f"/ 경로에 대한 요청 수신, 호스트: {request.host}")
    return render_template('index.html', categories=CATEGORIES)

# 헬스체크 엔드포인트 추가
@app.route('/health')
def health():
    # 시스템 상태 확인
    api_key_status = "설정됨" if openai.api_key else "설정되지 않음"
    data_status = f"로드됨 ({len(data)}개 항목)" if data else "로드 실패"
    
    # 데이터 샘플 5개 포함
    data_sample = []
    if data:
        for i, item in enumerate(data[:5]):
            data_sample.append({
                "소분류": item.get("소분류", ""),
                "examples_count": len(item.get("examples", [])),
            })
    
    # 정적 데이터 확인
    extra_data_keys = list(extra_data.keys())
    
    return jsonify(
        status="ok", 
        message="서비스가 정상 작동 중입니다.",
        api_key_status=api_key_status,
        data_status=data_status,
        data_sample=data_sample,
        extra_data_keys=extra_data_keys,
        categories=CATEGORIES
    )

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '').strip()
    print(f"사용자 입력: '{message}'")
    
    # 정적 데이터 응답
    if message in extra_data:
        answer = extra_data[message]
        return jsonify(bot=answer, options=POST_OPTIONS)
        
    # 견체공학 소개 관련 키워드 질문 처리
    if "견체공학" in message and ("뭔가요" in message or "무엇" in message or "소개" in message or "어떤" in message):
        print("견체공학 소개 관련 질문 감지됨")
        answer = extra_data["견체공학 소개"]
        return jsonify(bot=answer, options=POST_OPTIONS)
        
    # 카테고리 선택 처리
    if message in ['어부바가방', '견글라스']:
        # 관련 소분류 추출
        rows = [row for row in data if message in row['챗봇 답변']]
        subcats = list(dict.fromkeys([row['소분류'] for row in rows]))
        return jsonify(bot='어떤 정보를 원하시나요?', options=subcats)
    # 소분류 선택 처리
    for row in data:
        if message == row['소분류']:
            answer = row['챗봇 답변'].strip()
            return jsonify(bot=answer + '\n\n더 도움이 필요하면 상담원 연결을 요청해주세요.', options=POST_OPTIONS)
    
    # 자유 입력 처리: 유사도 검색 + AI 응답
    best_score = 0.0
    best_row = None
    scores = []
    for row in data:
        for ex in row['examples']:
            score = difflib.SequenceMatcher(None, message, ex).ratio()
            scores.append((score, ex, row['소분류']))
            if score > best_score:
                best_score = score
                best_row = row
    # 점수 내림차순 정렬 및 상위 3개 출력
    top_scores = sorted(scores, key=lambda x: x[0], reverse=True)[:3]
    print(f"유사도 상위 3개: {top_scores}")
    print(f"최고 점수: {best_score}, 임계값: 0.4")
    
    # OpenAI API로 답변 생성
    try:
        # 시스템 프롬프트 구성
        system_prompt = f"""당신은 견체공학 브랜드의 공식 챗봇 도우미입니다.
다음 브랜드 정보와 응답 지침을 바탕으로 질문에 답변하세요:

### 브랜드 정보:
{BRAND_CONTEXT}

### 응답 지침:
{RESPONSE_GUIDELINES}

위 내용을 기반으로 답변하되, 자연스럽고 따뜻한 어조를 유지하세요. 
불확실한 정보는 말하지 말고, 간결하면서도 유용한 정보를 제공하세요.
고객의 질문에 충분히 상세하게 답변하고, 관련된 추가 정보도 적절히 제공하세요.
단순 나열보다는 문장으로 된 충실한 설명을 제공하세요."""
        
        # 유사도 높은 경우 해당 정보도 포함
        if best_row and best_score > 0.3:
            additional_info = f"""
또한, 질문과 관련이 있는 다음 정보도 참고하세요:
{best_row['챗봇 답변']}
"""
            system_prompt += additional_info
        
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=520,
            temperature=0.6
        )
        
        answer = response.choices[0].message['content'].strip()
        print(f"AI 응답: {answer[:50]}...")
        
        # 답변에 상담원 연결 안내가 없는 경우에만 추가
        if "상담원 연결" not in answer:
            answer += '\n\n더 도움이 필요하면 상담원 연결을 요청해주세요.'
            
        return jsonify(bot=answer, options=POST_OPTIONS)
    
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        
        # API 오류 시 기존 방식으로 폴백
        if best_row and best_score > 0.4:
            ans = best_row['챗봇 답변'].strip()
            print(f"폴백 - 선택된 답변: {ans[:30]}...")
            return jsonify(bot=ans + '\n\n더 도움이 필요하면 상담원 연결을 요청해주세요.', options=POST_OPTIONS)
        
        # API 오류 + 견체공학 관련 질문인 경우 기본 정보 제공
        if "견체공학" in message:
            print("API 오류 발생, 견체공학 기본 정보 제공")
            answer = f"""견체공학은 반려견과 보호자의 편안함을 최우선으로 생각하는 프리미엄 반려동물 용품 브랜드입니다.

주요 제품으로는 어부바가방(중형견 가방 시장 9년 연속 1위)과 견글라스(강아지용 선글라스)가 있습니다. 

어부바가방은 반려견의 체형에 맞춘 인체공학적 설계로 이동 시 반려견의 편안함을 극대화했으며, 보호자의 부담도 최소화했습니다. 프리미엄형 어부바3와 알뜰형 어부바라이트2 모델이 있습니다.

견글라스는 자외선으로부터 반려견의 눈을 보호하는 전문 제품으로, 강아지 머리 둘레에 따라 S, M, L 사이즈로 구분됩니다. 토탈 케어 서비스로 프레임/렌즈 교체와 무상 수리 서비스도 제공합니다.

더 도움이 필요하면 상담원 연결을 요청해주세요."""
            return jsonify(bot=answer, options=POST_OPTIONS)
        
        # 이해 못했을 때
        return jsonify(bot='죄송합니다, 질문을 완전히 이해하지 못했어요. 어부바가방, 견글라스, 견체공학 소개 등 원하시는 정보를 선택하시거나 다른 질문을 해주시면 더 도움이 될 것 같아요. 선택지를 다시 안내드릴게요!', options=CATEGORIES)

@app.route('/ping_ai')
def ping_ai():
    try:
        models = openai.Model.list()
        return jsonify(status='ok', models=[m.id for m in models.data[:5]])
    except Exception as e:
        return jsonify(status='error', error=str(e)), 500

if __name__ == '__main__':
    # 로컬 개발 환경에서만 실행됨
    # Render.com에서는 gunicorn이 app 객체를 직접 사용
    app.run(host='0.0.0.0', port=port) 