import os
import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import random


# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# 대화 기록 저장
chat_history = []

class SimpleNLPModel:
    def __init__(self):
        pass

    def classify_intent(self, text):
        # 간단한 규칙 기반 의도 분류
        text = text.lower()

        # 기본적인 키워드 매칭
        greeting_keywords = ['안녕', '하이', '반가워', 'hello', 'hi']
        question_keywords = ['뭐', '무엇', '어떻게', '왜', '어떤', '언제', '누구', '어디', '?', '까']

        if any(keyword in text for keyword in greeting_keywords):
            return 'greeting'
        elif any(keyword in text for keyword in question_keywords):
            return 'question'
        else:
            return 'unknown'

    def generate_response(self, text):
        try:
            # 의도 분류
            intent = self.classify_intent(text)

            # 응답 템플릿에서 무작위 선택
            response = random.choice(RESPONSE_TEMPLATES[intent])

            # 질문인 경우 입력 텍스트의 키워드를 포함
            if intent == 'question':
                keywords = [word for word in text.split() if len(word) > 1]
                if keywords:
                    response += f"\n관련 키워드: {', '.join(keywords[:3])}"

            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return random.choice(RESPONSE_TEMPLATES['unknown'])

# NLP 모델 인스턴스 생성
nlp_model = SimpleNLPModel()

@app.route('/')
def home():
    return render_template('index.html', chat_history=chat_history)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # NLP 모델을 사용하여 응답 생성
        ai_message = nlp_model.generate_response(user_message)

        # 대화 기록에 추가
        timestamp = datetime.now().strftime("%H:%M")
        chat_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': timestamp
        })
        chat_history.append({
            'role': 'assistant',
            'content': ai_message,
            'timestamp': timestamp
        })

        return jsonify({
            'response': ai_message,
            'timestamp': timestamp
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': '죄송합니다. 처리 중 오류가 발생했습니다. 다시 시도해주세요.'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)