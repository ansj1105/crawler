#!/bin/bash

# PM2 관리 스크립트

case "$1" in
    start)
        echo "PM2 앱 시작 중..."
        
        # 로그 디렉토리 생성
        mkdir -p logs
        
        # 실행 권한 부여
        chmod +x run_crawler.sh
        
        # PM2로 앱 시작
        pm2 start ecosystem.config.js
        
        # 상태 확인
        pm2 status
        
        # 설정 저장 (재부팅 시 자동 시작)
        pm2 save
        ;;
        
    stop)
        echo "PM2 앱 중지 중..."
        pm2 stop all
        ;;
        
    restart)
        echo "PM2 앱 재시작 중..."
        pm2 restart all
        ;;
        
    status)
        echo "PM2 상태 확인..."
        pm2 status
        ;;
        
    logs)
        echo "PM2 로그 확인..."
        if [ -n "$2" ]; then
            pm2 logs "$2"
        else
            pm2 logs
        fi
        ;;
        
    delete)
        echo "PM2 앱 삭제 중..."
        pm2 delete all
        ;;
        
    monitor)
        echo "PM2 모니터링..."
        pm2 monit
        ;;
        
    *)
        echo "사용법: $0 {start|stop|restart|status|logs|delete|monitor}"
        echo ""
        echo "  start   - 웹서버와 크롤러 시작"
        echo "  stop    - 모든 프로세스 중지"
        echo "  restart - 모든 프로세스 재시작"
        echo "  status  - 프로세스 상태 확인"
        echo "  logs    - 로그 확인 (logs [앱이름])"
        echo "  delete  - 모든 프로세스 삭제"
        echo "  monitor - 실시간 모니터링"
        exit 1
        ;;
esac 