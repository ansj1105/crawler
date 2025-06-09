#!/bin/bash

# 크롤러 실행 스크립트

# 스크립트 디렉토리로 이동
cd /var/test/crawl/crawler

# 로그 시작
echo "=== 크롤러 시작: $(date) ==="

# Python 크롤러 실행
python3 crawl_and_save.py

# 실행 결과 확인
if [ $? -eq 0 ]; then
    echo "=== 크롤러 완료: $(date) ==="
else
    echo "=== 크롤러 오류: $(date) ==="
fi

echo "" 