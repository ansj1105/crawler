#!/bin/bash

# Ubuntu에서 Chrome 브라우저 설치 스크립트

echo "Chrome 브라우저 설치 중..."

# 시스템 업데이트
sudo apt update

# 필요한 패키지 설치
sudo apt install -y wget gnupg unzip

# Google Chrome 저장소 키 추가
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# Google Chrome 저장소 추가
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list

# 패키지 목록 업데이트
sudo apt update

# Google Chrome 설치
sudo apt install -y google-chrome-stable

# 설치 확인
echo "Chrome 설치 완료!"
google-chrome --version

# 추가 의존성 설치 (headless 모드용)
sudo apt install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1

echo "Chrome 브라우저 설치 및 의존성 설정 완료!" 