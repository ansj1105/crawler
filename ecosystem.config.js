module.exports = {
  apps: [
    {
      // Flask 웹 서버
      name: 'crawler-web',
      script: 'python3',
      args: 'app.py',
      cwd: '/var/test/crawl/crawler',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        FLASK_ENV: 'production'
      },
      error_file: './logs/web-error.log',
      out_file: './logs/web-out.log',
      log_file: './logs/web-combined.log',
      time: true
    },
    {
      // 크롤러 스케줄러 (30분마다 실행)
      name: 'crawler-scheduler',
      script: '/var/test/crawl/crawler/run_crawler.sh',
      cwd: '/var/test/crawl/crawler',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      cron_restart: '*/30 * * * *', // 30분마다 실행
      max_memory_restart: '300M',
      error_file: './logs/crawler-error.log',
      out_file: './logs/crawler-out.log',
      log_file: './logs/crawler-combined.log',
      time: true
    }
  ]
}; 