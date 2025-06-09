import os
import time
import datetime
import socket
import json
import urllib.request
import urllib.parse
import requests
import platform

import mysql.connector
from mysql.connector import Error
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import wikipedia

#from flask import Flask, request, jsonify

load_dotenv()
# env load (기본값 설정)
SSH_HOST = os.getenv("SSH_HOST", "localhost")
SSH_PORT = int(os.getenv("SSH_PORT", "22"))
SSH_USER = os.getenv("SSH_USER", "user")
SSH_PRIVATE_KEY = os.getenv("SSH_PRIVATE_KEY", "")

DB_HOST_INTERNAL = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT_INTERNAL = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'vietcoin')
DB_PASS = os.getenv('DB_PASS', 'vietcoin1234!')
DB_NAME = os.getenv('DB_NAME', 'craw_test')
LOCAL_BIND_HOST = os.getenv("LOCAL_BIND_HOST", "127.0.0.1")
LOCAL_BIND_PORT = int(os.getenv("LOCAL_BIND_PORT", "3306"))

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

# OS별 ChromeDriver 경로 자동 설정
def get_chromedriver_path():
    current_os = platform.system()
    if current_os == "Windows":
        return os.path.join(os.getcwd(), "chromedriver", "chromedriver.exe")
    elif current_os == "Darwin":  # macOS
        return os.path.join(os.getcwd(), "chromedriver", "chromedriver")
    else:  # Linux (Ubuntu)
        linux_path = os.path.join(os.getcwd(), "chromedriver", "chromedriver-linux")
        if os.path.exists(linux_path):
            return linux_path
        else:
            return os.path.join(os.getcwd(), "chromedriver", "chromedriver")

CHROMEDRIVER_PATH = get_chromedriver_path()
WEBSITES = {
    "NAVER_DATALAB":     "https://datalab.naver.com/keyword/realtimeList.naver?where=main",
    "SIGNAL_BZ":         "https://signal.bz/",
    "GOOGLE_TRENDS_KR":  "https://trends.google.co.kr/trending?geo=KR"
}
SIG_URL = WEBSITES["SIGNAL_BZ"]
wikipedia.set_lang('ko')

# 6/5 : using this function is not fixed
def make_candidates_from_phrase(phrase:str) -> list[str]:
    # change to konlpy??시간 남으면 ..
    cleaned = (
        phrase.replace("(", " ")
              .replace(")", " ")
              .replace(",", " ")
              .replace(".", " ")
              .strip()
    )
    raw_tokens = cleaned.split()
    single_tokens = []
    for tok in raw_tokens:
        if len(tok) < 2:
            continue
        if tok.isnumeric():
            continue
        single_tokens.append(tok)

    n = len(single_tokens)
    two_tokens = set()
    for i in range(n-1):
        joined = f"{single_tokens[i]} {single_tokens[i+1]}"
        two_tokens.add(joined)
    return single_tokens + list(two_tokens)

# 6/5 : added article api
def get_article_info(encText:str, max_articles: int=5) -> list:    
    encText = urllib.parse.quote(encText)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={max_articles}"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode != 200:
            print(f"Error: HTTP {rescode}")
            return []
        response_body = response.read().decode("utf-8")
        print(response_body)    # debug point
        data = json.loads(response_body)
        items = data.get("items", [])
        articles = []
        for it in items:
            # html parsing
            title_html = it.get("title", "")
            title_text = BeautifulSoup(title_html, "html.parser").get_text()

            link = it.get("link", "")
            desc_html = it.get("description", "")
            desc_text = BeautifulSoup(desc_html, "html.parser").get_text()

            pub_date = it.get("pubDate", "")
            articles.append({
                "title":title_text,
                "url":link,
                "summary":desc_text,
                "pubDate":pub_date
            })
        return articles
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"URLError : {e.reason}")
    except Exception as e:
        print(f"Unexpected error:[ {e} ]")
    return []

def save_topic_and_articles(website_name:str, base_url:str, title:str, content:str, views:int, comments:int, wiki_page_title:str, articles: list[dict], conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT website_id FROM websites WHERE name = %s", (website_name,))
        row = cursor.fetchone()
        if row:
            website_id = row[0]
        else:
            cursor.execute("INSERT INTO websites (name, url) VALUES (%s, %s)" ,(website_name, base_url))
            conn.commit()
            website_id = cursor.lastrowid
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sql_topic = """
            INSERT INTO Topics (website_id, title, content, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at)
        """
        cursor.execute(sql_topic, (website_id, title, content, now, now))
        conn.commit()

        cursor.execute(
            "SELECT topic_id FROM Topics WHERE website_id=%s AND title=%s AND created_at=%s",
            (website_id, title, now)
        )
        topic_row = cursor.fetchone()
        if not topic_row:
            print("[DB] topic_id 조회 실패:", title)
            return
        topic_id = topic_row[0]
        sql_metric = """
            INSERT INTO Metrics (topic_id, views, comments, recorded_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE views = VALUES(views), comments = VALUES(comments)
        """
        cursor.execute(sql_metric, (topic_id, views, comments, now))
        conn.commit()
        sql_article = """
            INSERT INTO Articles 
              (topic_id, title, url, summary, pub_date, saved_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              summary = VALUES(summary),
              pub_date = VALUES(pub_date)
        """
        for art in articles:
            art_title   = art.get("title", "")[:255]
            art_url     = art.get("url", "")
            art_summary = art.get("summary", "")[:1000]
            art_pubdate = art.get("pubDate", "")
            cursor.execute(sql_article, (
                topic_id,
                art_title,
                art_url,
                art_summary,
                art_pubdate,
                now
            ))
        conn.commit()

    except Error as e:
        print("[DB] Error while saving:", e)
    finally:
        cursor.close()
    

def fetch_wikipedia_person_info(name: str) -> dict:
    result = {"exists":False}
    try:
        search_results = wikipedia.search(name, results=1)
    except Exception:
        return result
    
    if not search_results:
        return result
    
    candidate_title = search_results[0]
    try:
        page = wikipedia.page(candidate_title, auto_suggest=False)
    except (wikipedia.DisambiguationError, wikipedia.PageError):
        return result
    
    # 간단히 페이지 제목과 요약만 사용 (infobox 파싱 제거)
    summary = page.summary
    result.update({
        "exists": True,
        "page_title": page.title,
        "url": page.url,
        "summary": summary[:200] + "..." if len(summary) > 200 else summary,
        "occupation": ""  # 일단 빈 문자열로 설정
    })
    return result

def wait_for_port(host:str, port:int, timeout:float=5.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host,port), timeout=1):
                return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.2)
    return False

def get_db_connection():
    # SSH 터널 대신 직접 로컬 DB 연결
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="vietcoin",
            password="vietcoin1234!",
            database="craw_test",
            charset="utf8mb4",
            connection_timeout=10
        )
        return conn
    except Error as e:
        print("[DB] Connection error:", e)
        return None

def init_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=ko-KR")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def crawl_naver_datalab(driver):
    """
    url = "https://datalab.naver.com/keyword/realtimeList.naver?where=main"
    driver.get(url)
    time.sleep(2)
    try:
        html = driver.page_source
        with open("debug_naver.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[Debug] Naver DataLab - page_source saved to debug_naver.html")
    except Exception as e:
        print("[Debug Error] Failed to dump page_source:", e)

    items = []
    try:
        titles = driver.find_elements(By.CSS_SELECTOR, ".ranking_list .list_area li .item_title")
        counts = driver.find_elements(By.CSS_SELECTOR, ".ranking_list .list_area li .item_num")
        print(f"[Debug] Naver DataLab - titles found: {len(titles)}, counts found: {len(counts)}")
    except Exception as e:
        print(f"[Crawl Error - Naver DataLab] {e}")
    
    return items
    """

def crawl_signal_bz(driver):
    url = "https://signal.bz/"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".rank-text"))
        )
        print("[Debug] Signal.bz - '.rank-text' appeared in DOM")
    except Exception as e:
        print("[Debug] Signal.bz - Timeout waiting for .rank-text:", e)
        return []

    items = []
    try:
        title_elems = driver.find_elements(By.CSS_SELECTOR, ".rank-text")
        num_elems   = driver.find_elements(By.CSS_SELECTOR, ".rank-num")
        print(f"[Debug] Signal.bz - titles found: {len(title_elems)}, nums found: {len(num_elems)}")

        for title_elem, num_elem in zip(title_elems, num_elems):
            title_text = title_elem.text.strip()
            rank_num   = num_elem.text.strip()  
            views = 0       
            comments = 0    

            if title_text:
                items.append((title_text, "", views, comments))
    except Exception as e:
        print(f"[Crawl Error - Signal.bz] {e}")

    return items

def crawl_google_trends(driver):
    url = "https://trends.google.co.kr/trending?geo=KR"
    #driver.get(url)
    #time.sleep(2)

    items = []
    """
    try:
        titles = driver.find_elements(By.CSS_SELECTOR, ".feed-list-wrapper .feed-item-container .details-text")
        print(f"[Debug] Google Trends - titles found: {len(titles)}")

        for title_elem in titles:
            title_text = title_elem.text.strip()
            views = 0
            comments = 0
            if title_text:
                items.append((title_text, "", views, comments))
    except Exception as e:
        print(f"[Crawl Error - Google Trends] {e}")
    """
    return items

def query_celebrity_naver(keyword: str):
    # checks if input keyword:str is celebrity
        # returns : (is_celebrity, total_count, celeb_data_list, error_msg)
        api_url = "https://openapi.naver.com/v1/search/celebrity.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        params = {
            "query": keyword,
            "display": 1
        }
        
        try:
            resp = requests.get(api_url, headers=headers, params=params, timeout=6)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            return False,0,[],f"API Call Fail:{e}"
        data=resp.json()
        total=data.get("total",0)
        items=data.get("items", [])
        if total > 0 and len(items) > 0:
            return True, total, items, ""
        else:
            return False, total, [], "No Search Result"


# ───────────────────────────────────────────────────────────────────
def save_crawled_data(website_name, base_url, crawled_items):
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT website_id FROM websites WHERE name = %s", (website_name,))
        row = cursor.fetchone()
        if row:
            website_id = row[0]
        else:
            cursor.execute(
                "INSERT INTO websites (name, url) VALUES (%s, %s)",
                (website_name, base_url)
            )
            conn.commit()
            website_id = cursor.lastrowid
            print(f"[DB] Inserted new website '{website_name}' with ID {website_id}")

        saved_count = 0
        for title, content, view_cnt, comment_cnt in crawled_items:
            now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            sql_topic = """
                INSERT INTO Topics (website_id, title, content, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title = title
            """
            cursor.execute(sql_topic, (website_id, title, content, now, now))
            conn.commit()

            cursor.execute(
                "SELECT topic_id FROM Topics WHERE website_id=%s AND title=%s AND created_at=%s",
                (website_id, title, now)
            )
            topic_row = cursor.fetchone()
            if not topic_row:
                print("[DB] Failed to fetch topic_id for:", title)
                continue
            topic_id = topic_row[0]

            sql_metric = """
                INSERT INTO Metrics (topic_id, views, comments, recorded_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  views    = VALUES(views),
                  comments = VALUES(comments)
            """
            cursor.execute(sql_metric, (topic_id, view_cnt, comment_cnt, now))
            conn.commit()

            saved_count += 1

        print(f"[DB] Saved {saved_count} rows into Topics/Metrics for '{website_name}'.")

    except Error as e:
        print("[DB] Error while saving crawled data:", e)
    finally:
        cursor.close()
        conn.close()

def print_saved_data(website_name, limit=10):
    conn = get_db_connection()
    if conn is None:
        return

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
        WHERE w.name = %s
        ORDER BY t.created_at DESC
        LIMIT %s;
        """
        cursor.execute(sql, (website_name, limit))
        rows = cursor.fetchall()

        print(f"--- Saved data for '{website_name}' (limit {limit} rows) ---")
        for row in rows:
            print(
                f"[{row['website_name']}] "
                f"TITLE: \"{row['title']}\" | "
                f"CONTENT: \"{row['content'][:50]}...\" | "
                f"VIEWS: {row['view_count']} | "
                f"COMMENTS: {row['comment_count']} | "
                f"CREATED_AT: {row['topic_created']} | "
                f"METRIC_AT: {row['metric_recorded']}"
            )

    except Error as e:
        print("[DB] Error while fetching saved data:", e)
    finally:
        cursor.close()
        conn.close()


def main():
    driver = init_chrome_driver()
    try:
        signal_items = crawl_signal_bz(driver)
        print(f"크롤링된 아이템: {len(signal_items)}개")
        
        # 간단히 크롤링된 데이터만 저장
        save_crawled_data("SIGNAL_BZ", WEBSITES["SIGNAL_BZ"], signal_items)
        print_saved_data("SIGNAL_BZ", limit=10)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
