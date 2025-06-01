import os
import time
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import mysql.connector
from mysql.connector import Error


DB_HOST   = "127.0.0.1"
DB_PORT   = 3307
DB_USER   = ""
DB_PASS   = ""
DB_NAME   = ""

#CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", os.path.join(os.getcwd(), "chromedriver", "chromedriver.exe"))
CHROMEDRIVER_PATH = r"C:\Users\mbaek\OneDrive\바탕 화면\대학교\4학년\1학기\융합SW프로젝트\Workspace\dc\chromedriver\chromedriver.exe"
WEBSITES = {
    "NAVER_DATALAB":     "https://datalab.naver.com/keyword/realtimeList.naver?where=main",
    "SIGNAL_BZ":         "https://signal.bz/",
    "GOOGLE_TRENDS_KR":  "https://trends.google.co.kr/trending?geo=KR"
}
SIG_URL = WEBSITES["SIGNAL_BZ"]
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
        #naver_items = crawl_naver_datalab(driver)
        signal_items = crawl_signal_bz(driver)
        #trends_items = crawl_google_trends(driver)
    finally:
        driver.quit()
    #save_crawled_data("NAVER_DATALAB", WEBSITES["NAVER_DATALAB"], naver_items)
    save_crawled_data("SIGNAL_BZ",   WEBSITES["SIGNAL_BZ"],   signal_items)
    #save_crawled_data("GOOGLE_TRENDS_KR", WEBSITES["GOOGLE_TRENDS_KR"], trends_items)

    #print_saved_data("NAVER_DATALAB", limit=10)
    print_saved_data("SIGNAL_BZ",   limit=10)
    #print_saved_data("GOOGLE_TRENDS_KR", limit=10)

if __name__ == "__main__":
    main()
