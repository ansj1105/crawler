from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from google.cloud import translate_v2 as translate
import os


DB_HOST   = "127.0.0.1"
DB_PORT=3306
DB_USER="vietcoin"
DB_PASS="vietcoin1234!"
DB_NAME="craw_test"



def get_db_connection():

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        print("[DB] Connection error:", e)
        return None

app = Flask(__name__)

# Google Translate 클라이언트 초기화
try:
    translate_client = translate.Client()
except Exception as e:
    print(f"Google Translate 초기화 실패: {e}")
    translate_client = None

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DCProject Crawler Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 25px;
                padding: 60px 40px;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                text-align: center;
            }
            
            .logo {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            
            h1 {
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 15px;
            }
            
            .subtitle {
                color: #666;
                font-size: 1.3rem;
                margin-bottom: 50px;
                line-height: 1.6;
            }
            
            .button-group {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                padding: 18px 30px;
                border-radius: 15px;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
                min-width: 200px;
                justify-content: center;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
            }
            
            .btn-secondary {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
            }
            
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
            }
            
            .features {
                margin-top: 50px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 30px;
            }
            
            .feature {
                padding: 25px;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 15px;
            }
            
            .feature h3 {
                color: #333;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }
            
            .feature p {
                color: #666;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 40px 25px;
                }
                
                h1 {
                    font-size: 2.5rem;
                }
                
                .button-group {
                    flex-direction: column;
                    align-items: center;
                }
                
                .btn {
                    width: 100%;
                    max-width: 300px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚀</div>
            <h1>DCProject Crawler</h1>
            <p class="subtitle">
                실시간 트렌딩 키워드를 수집하고 분석하는<br>
                지능형 웹 크롤링 대시보드
            </p>
            
            <div class="button-group">
                <a href="/topics" class="btn btn-primary">
                    <span>📊</span>
                    대시보드 보기
                </a>
                <a href="/topics/translate/en" class="btn btn-secondary">
                    <span>🌍</span>
                    다국어 번역
                </a>
                <a href="/api/topics" class="btn btn-secondary">
                    <span>⚡</span>
                    API 데이터
                </a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🔄</div>
                    <h3>자동 크롤링</h3>
                    <p>30분마다 자동으로 최신 트렌딩 키워드를 수집합니다</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📈</div>
                    <h3>실시간 분석</h3>
                    <p>수집된 데이터를 실시간으로 분석하고 시각화합니다</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌐</div>
                    <h3>다중 소스</h3>
                    <p>다양한 웹사이트에서 트렌딩 정보를 종합적으로 수집</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/api/topics")
def api_get_topics():
    conn = get_db_connection()
    if conn is None:
        return {"error": "DB 연결 실패"}, 500

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT
          w.name            AS website_name,
          t.title           AS title,
          t.content         AS content,
          m.views           AS view_count,
          m.comments        AS comment_count,
          t.created_at      AS topic_created,
          m.recorded_at     AS metric_recorded
        FROM Topics AS t
        JOIN websites AS w   ON t.website_id = w.website_id
        JOIN Metrics  AS m   ON t.topic_id     = m.topic_id
        ORDER BY t.created_at DESC
        LIMIT 100;
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return {"topics": rows}, 200

    except Error as e:
        print("[DB] Error in /api/topics:", e)
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        conn.close()

@app.route("/topics")
def page_topics():
    conn = get_db_connection()
    if conn is None:
        return "<h2>DB 연결 실패</h2>"

    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT
          w.name            AS website_name,
          t.title           AS title,
          t.content         AS content,
          m.views           AS view_count,
          m.comments        AS comment_count,
          t.created_at      AS topic_created,
          m.recorded_at     AS metric_recorded
        FROM Topics AS t
        JOIN websites AS w   ON t.website_id = w.website_id
        JOIN Metrics  AS m   ON t.topic_id     = m.topic_id
        ORDER BY t.created_at DESC
        LIMIT 100;
        """
        cursor.execute(sql)
        topics = cursor.fetchall()
        return render_template("topics.html", topics=topics)

    except Error as e:
        print("[DB] Error in /topics:", e)
        return f"<h2>DB 조회 오류: {e}</h2>"

    finally:
        cursor.close()
        conn.close()

@app.route("/api/topics/translate")
@app.route("/api/topics/translate/<lang_code>")
def api_translate_topics(lang_code='en'):
    """
    Topics의 title을 지정된 언어로 번역하여 반환
    지원 언어: en(영어), ja(일본어), zh(중국어), fr(프랑스어), es(스페인어), de(독일어) 등
    """
    # URL 파라미터로도 언어 지정 가능
    if 'lang' in request.args:
        lang_code = request.args.get('lang', 'en')
    
    # 번역 클라이언트가 없으면 에러 반환
    if translate_client is None:
        return {"error": "번역 서비스를 사용할 수 없습니다"}, 500
    
    # 지원 언어 목록
    supported_languages = {
        'en': 'English',
        'ja': 'Japanese', 
        'zh': 'Chinese',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'ru': 'Russian',
        'pt': 'Portuguese',
        'it': 'Italian',
        'ko': 'Korean'
    }
    
    if lang_code not in supported_languages:
        return {
            "error": f"지원하지 않는 언어입니다. 지원 언어: {list(supported_languages.keys())}"
        }, 400

    conn = get_db_connection()
    if conn is None:
        return {"error": "DB 연결 실패"}, 500

    cursor = conn.cursor(dictionary=True)
    try:
        # 제한된 수의 최신 토픽만 가져오기 (번역 비용 절약)
        limit = int(request.args.get('limit', 50))
        if limit > 100:
            limit = 100
            
        sql = """
        SELECT
          w.name            AS website_name,
          t.title           AS title,
          t.content         AS content,
          m.views           AS view_count,
          m.comments        AS comment_count,
          t.created_at      AS topic_created,
          m.recorded_at     AS metric_recorded
        FROM Topics AS t
        JOIN websites AS w   ON t.website_id = w.website_id
        JOIN Metrics  AS m   ON t.topic_id     = m.topic_id
        ORDER BY t.created_at DESC
        LIMIT %s;
        """
        cursor.execute(sql, (limit,))
        topics = cursor.fetchall()
        
        # 번역 작업
        translated_topics = []
        translation_errors = []
        
        for topic in topics:
            try:
                original_title = topic['title']
                
                # 한국어가 아닌 경우에만 번역 (이미 한국어면 번역 안함)
                if lang_code == 'ko':
                    translated_title = original_title
                else:
                    # Google Translate API 호출
                    result = translate_client.translate(
                        original_title,
                        target_language=lang_code,
                        source_language='ko'  # 소스가 한국어라고 가정
                    )
                    translated_title = result['translatedText']
                
                # 번역된 정보 추가
                topic_with_translation = topic.copy()
                topic_with_translation.update({
                    'original_title': original_title,
                    'translated_title': translated_title,
                    'target_language': lang_code,
                    'language_name': supported_languages[lang_code]
                })
                
                translated_topics.append(topic_with_translation)
                
            except Exception as e:
                translation_errors.append({
                    'title': topic['title'],
                    'error': str(e)
                })
                # 번역 실패해도 원본 제목으로 추가
                topic_with_translation = topic.copy()
                topic_with_translation.update({
                    'original_title': topic['title'],
                    'translated_title': topic['title'],  # 번역 실패시 원본 사용
                    'target_language': lang_code,
                    'language_name': supported_languages[lang_code],
                    'translation_error': str(e)
                })
                translated_topics.append(topic_with_translation)

        response_data = {
            "target_language": lang_code,
            "language_name": supported_languages[lang_code],
            "total_topics": len(translated_topics),
            "topics": translated_topics
        }
        
        if translation_errors:
            response_data["translation_errors"] = translation_errors
            
        return response_data, 200

    except Error as e:
        print("[DB] Error in /api/topics/translate:", e)
        return {"error": str(e)}, 500

    finally:
        cursor.close()
        conn.close()

@app.route("/api/languages")
def api_supported_languages():
    """지원하는 번역 언어 목록 반환"""
    languages = {
        'ko': '한국어 (Korean)',
        'en': '영어 (English)',
        'ja': '일본어 (Japanese)', 
        'zh': '중국어 (Chinese)',
        'fr': '프랑스어 (French)',
        'es': '스페인어 (Spanish)',
        'de': '독일어 (German)',
        'ru': '러시아어 (Russian)',
        'pt': '포르투갈어 (Portuguese)',
        'it': '이탈리아어 (Italian)'
    }
    
    return {
        "supported_languages": languages,
        "usage_examples": [
            "/api/topics/translate/en - 영어로 번역",
            "/api/topics/translate/ja - 일본어로 번역", 
            "/api/topics/translate?lang=zh&limit=20 - 중국어로 번역 (20개 제한)"
        ]
    }, 200

@app.route("/topics/translate")
@app.route("/topics/translate/<lang_code>")
def page_translated_topics(lang_code='en'):
    """번역된 토픽을 보여주는 웹 페이지"""
    # URL 파라미터로도 언어 지정 가능
    if 'lang' in request.args:
        lang_code = request.args.get('lang', 'en')
    
    # API에서 번역된 데이터 가져오기
    try:
        # 내부적으로 번역 API 호출
        response_data, status_code = api_translate_topics(lang_code)
        
        if status_code != 200:
            return f"<h2>번역 오류: {response_data.get('error', '알 수 없는 오류')}</h2>"
        
        return render_template("translated_topics.html", 
                             topics=response_data['topics'],
                             target_language=response_data['target_language'],
                             language_name=response_data['language_name'],
                             total_topics=response_data['total_topics'])
                             
    except Exception as e:
        return f"<h2>페이지 로드 오류: {str(e)}</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)