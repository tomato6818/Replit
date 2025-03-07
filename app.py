import os
import logging
from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from datetime import datetime
import random

# NLTK 데이터 다운로드
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# 간단한 응답 템플릿
RESPONSE_TEMPLATES = {
    'greeting': [
        "안녕하세요! 무엇을 도와드릴까요?",
        "반갑습니다! 어떤 것이 궁금하신가요?",
        "좋은 하루입니다! 무엇이 필요하신가요?"
    ],
    'question': [
        "흥미로운 질문이네요. 제가 알고 있는 내용을 공유해드리겠습니다:",
        "좋은 질문입니다! 다음과 같이 답변드릴 수 있습니다:",
        "그것에 대해 설명드리겠습니다:"
    ],
    'unknown': [
        "죄송합니다. 질문의 의도를 정확히 파악하지 못했습니다. 다르게 표현해주시겠어요?",
        "더 자세히 설명해주시면 더 나은 답변을 드릴 수 있을 것 같습니다.",
        "죄송하지만 그 부분에 대해서는 확실하지 않습니다. 다른 방식으로 질문해주시겠어요?"
    ]
}

# TF-IDF 벡터라이저 초기화
vectorizer = TfidfVectorizer(max_features=1000)

# 대화 기록 저장
chat_history = []

class SimpleNLPModel:
    def __init__(self):
        self.lemmatizer = nltk.WordNetLemmatizer()

    def preprocess_text(self, text):
        # 토큰화
        tokens = nltk.word_tokenize(text)
        # 품사 태깅
        tagged = nltk.pos_tag(tokens)
        # 레마타이제이션
        lemmatized = [self.lemmatizer.lemmatize(word) for word, tag in tagged]
        return ' '.join(lemmatized)

    def classify_intent(self, text):
        # 간단한 규칙 기반 의도 분류
        text = text.lower()
        if any(word in text for word in ['안녕', '하이', '반가워']):
            return 'greeting'
        elif any(word in text for word in ['뭐', '무엇', '어떻게', '왜', '어떤']):
            return 'question'
        else:
            return 'unknown'

    def generate_response(self, text):
        # 텍스트 전처리
        processed_text = self.preprocess_text(text)
        # 의도 분류
        intent = self.classify_intent(text)
        # 응답 템플릿에서 무작위 선택
        template = random.choice(RESPONSE_TEMPLATES[intent])

        if intent == 'question':
            # TF-IDF를 사용한 키워드 추출
            tfidf = vectorizer.fit_transform([processed_text])
            feature_names = vectorizer.get_feature_names_out()
            important_words = [feature_names[i] for i in tfidf.toarray()[0].argsort()[-3:][::-1]]

            # 키워드를 포함한 응답 생성
            response = f"{template}\n관련 키워드: {', '.join(important_words)}"
        else:
            response = template

        return response

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