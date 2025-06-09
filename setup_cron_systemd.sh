#!/bin/bash

# Cron + Systemd 설정 스크립트

echo "Cron + Systemd 설정 중..."

# 1. Flask 웹서버용 systemd 서비스 생성
sudo tee /etc/systemd/system/crawler-web.service > /dev/null <<EOF
[Unit]
Description=Crawler Web Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/test/crawl/crawler
ExecStart=/usr/bin/python3 /var/test/crawl/crawler/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 2. systemd 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable crawler-web
sudo systemctl start crawler-web

# 3. cron 작업 추가 (30분마다 크롤러 실행)
CRON_JOB="*/30 * * * * cd /var/test/crawl/crawler && /usr/bin/python3 crawl_and_save.py >> /var/test/crawl/crawler/logs/crawler.log 2>&1"

# 로그 디렉토리 생성
mkdir -p /var/test/crawl/crawler/logs

# cron 작업 추가
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "설정 완료!"
echo "웹서버 상태: sudo systemctl status crawler-web"
echo "cron 작업 확인: crontab -l" 