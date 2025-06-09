#!/bin/bash

# Ubuntu에서 ChromeDriver 설정 스크립트

echo "ChromeDriver 설정 중..."

# chromedriver 폴더로 이동
cd chromedriver

# Linux용 ChromeDriver 압축 해제
if [ -f "chromedriver-linux64.zip" ]; then
    echo "Linux용 ChromeDriver 압축 해제 중..."
    unzip -o chromedriver-linux64.zip
    
    # 파일명 변경
    if [ -f "chromedriver" ]; then
        mv chromedriver chromedriver-linux
        echo "ChromeDriver 파일명을 chromedriver-linux로 변경"
    fi
    
    # 실행 권한 부여
    chmod +x chromedriver-linux
    echo "실행 권한 부여 완료"
    
    # 파일 정보 확인
    echo "ChromeDriver 정보:"
    file chromedriver-linux
    ls -la chromedriver-linux
else
    echo "Error: chromedriver-linux64.zip 파일을 찾을 수 없습니다."
fi

cd ..

# Chrome 브라우저 설치 확인
echo "Chrome 브라우저 설치 확인 중..."
if command -v google-chrome &> /dev/null; then
    echo "Chrome 브라우저가 설치되어 있습니다."
    google-chrome --version
else
    echo "Chrome 브라우저가 설치되어 있지 않습니다."
    echo "다음 명령어로 설치하세요:"
    echo "sudo apt update"
    echo "sudo apt install -y wget gnupg"
    echo "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
    echo "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list"
    echo "sudo apt update"
    echo "sudo apt install -y google-chrome-stable"
fi

echo "설정 완료!" 