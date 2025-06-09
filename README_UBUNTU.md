# Ubuntu 서버에서 크롤러 설정 가이드

## 1. Chrome 브라우저 설치

```bash
# Chrome 설치 스크립트 실행
chmod +x install_chrome_ubuntu.sh
./install_chrome_ubuntu.sh
```

## 2. ChromeDriver 설정

```bash
# ChromeDriver 설정 스크립트 실행
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

## 3. Python 의존성 설치

```bash
# Python 패키지 설치
pip install -r requirements.txt
```

## 4. 데이터베이스 설정

MySQL 서버가 설치되어 있고 다음 설정으로 접근 가능한지 확인:
- Host: 127.0.0.1
- Port: 3306
- User: vietcoin
- Password: vietcoin1234!
- Database: craw_test

## 5. 크롤러 실행

```bash
python crawl_and_save.py
```

## 문제 해결

### ChromeDriver 오류
- `Exec format error`: Linux용 ChromeDriver가 제대로 설정되지 않음
- `Permission denied`: 실행 권한이 없음

```bash
# 수동으로 ChromeDriver 설정
cd chromedriver
unzip -o chromedriver-linux64.zip
mv chromedriver chromedriver-linux
chmod +x chromedriver-linux
```

### Chrome 브라우저 오류
- `chrome not found`: Chrome이 설치되지 않음
- 위의 Chrome 설치 스크립트 실행

### 의존성 오류
```bash
# 시스템 패키지 설치
sudo apt update
sudo apt install -y python3-pip mysql-server
```

## 환경변수 설정 (선택사항)

`.env` 파일을 생성하여 설정 변경:

```env
# 데이터베이스 설정
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=vietcoin
DB_PASS=vietcoin1234!
DB_NAME=craw_test

# ChromeDriver 경로 (자동 설정됨)
CHROMEDRIVER_PATH=./chromedriver/chromedriver-linux

# 네이버 API (선택사항)
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
``` 