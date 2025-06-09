from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error


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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)