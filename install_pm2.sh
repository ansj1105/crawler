#!/bin/bash

# PM2 설치 스크립트

echo "PM2 설치 중..."

# Node.js가 설치되어 있는지 확인
if ! command -v node &> /dev/null; then
    echo "Node.js 설치 중..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# PM2 전역 설치
sudo npm install -g pm2

# PM2 버전 확인
pm2 --version

# PM2 startup 설정 (시스템 부팅 시 자동 시작)
sudo pm2 startup systemd -u $USER --hp $HOME

echo "PM2 설치 완료!" 