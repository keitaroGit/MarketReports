# Deployment Guide - Market Reports Dashboard

本番環境へのデプロイメント手順を説明します。

## Docker を使用したデプロイ（推奨）

### 前提条件
- Docker がインストールされていること
- Docker Compose がインストールされていること
- 必要な API キーが揃っていること

### ステップ 1: 環境変数の設定
```bash
# .env ファイルに以下を設定
CLAUDE_API_KEY=your_claude_api_key
FRED_API_KEY=your_fred_api_key
NEWSAPI_KEY=your_newsapi_key
SECRET_KEY=your_secure_secret_key
FLASK_ENV=production
```

### ステップ 2: イメージのビルドと実行
```bash
# イメージをビルド
docker build -t market-reports-dashboard .

# コンテナを実行
docker run -d \
  --name market-reports \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/cache:/app/cache \
  market-reports-dashboard
```

### ステップ 3: Docker Compose を使用する場合
```bash
# サービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# サービスを停止
docker-compose down
```

## Gunicorn を使用した直接デプロイ

### 前提条件
- Python 3.8+ がインストールされていること
- 仮想環境が設定されていること

### ステップ 1: 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

### ステップ 2: Gunicorn で起動
```bash
# 基本的な起動
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 本番環境用（タイムアウト増加）
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app

# ソケットで起動
gunicorn -w 4 -k gevent --worker-connections 1000 \
  -b 0.0.0.0:5000 app:app
```

### ステップ 3: systemd サービスとして登録
```bash
# /etc/systemd/system/market-reports.service を作成
[Unit]
Description=Market Reports Dashboard
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/market-reports
Environment="PATH=/opt/market-reports/venv/bin"
Environment="FLASK_ENV=production"
EnvironmentFile=/opt/market-reports/.env
ExecStart=/opt/market-reports/venv/bin/gunicorn \
  -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# サービスを有効化
sudo systemctl enable market-reports
sudo systemctl start market-reports
sudo systemctl status market-reports
```

## Nginx 逆プロキシ設定

### Nginx 設定例
```nginx
upstream market_reports {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your_domain.com;

    # HTTPS リダイレクト（推奨）
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your_domain.com;

    # SSL 証明書（Let's Encrypt 推奨）
    ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://market_reports;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /opt/market-reports/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Nginx を再起動
```bash
sudo systemctl reload nginx
```

## AWS EC2 での デプロイ

### ステップ 1: インスタンスを起動
- Ubuntu 22.04 LTS を選択
- t3.medium 以上を推奨（4GB RAM）
- セキュリティグループで 443 ポートを開放

### ステップ 2: システムをセットアップ
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx
```

### ステップ 3: アプリケーションをデプロイ
```bash
cd /opt
sudo git clone <your-repo-url> market-reports
cd market-reports
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env を設定
sudo nano .env
```

### ステップ 4: systemd サービスを設定
```bash
sudo cp market-reports.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable market-reports
sudo systemctl start market-reports
```

### ステップ 5: SSL 証明書を取得
```bash
sudo certbot certonly --standalone -d your_domain.com
sudo certbot renew --dry-run
```

## AWS Lambda + API Gateway でのサーバーレスデプロイ

### Zappa を使用する場合
```bash
pip install zappa
zappa init

# デプロイ
zappa deploy production

# 更新
zappa update production
```

### zappa_settings.json の例
```json
{
    "production": {
        "django_settings_module": "config.production",
        "profile_name": "default",
        "project_name": "market-reports",
        "runtime": "python3.11",
        "s3_bucket": "your-zappa-bucket",
        "environment_variables": {
            "FLASK_ENV": "production"
        },
        "events": [{
            "function": "app.app",
            "expression": "rate(30 minutes)"
        }]
    }
}
```

## モニタリング と ログ管理

### CloudWatch ログ設定（AWS）
```python
# app.py に追加
import logging
from watchtower import CloudWatchLogHandler

if app.config['FLASK_ENV'] == 'production':
    log_handler = CloudWatchLogHandler()
    app.logger.addHandler(log_handler)
```

### ローカルログ設定
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/market_reports.log', 
                                      maxBytes=10240000, 
                                      backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## パフォーマンス最適化

### キャッシュの最適化
```bash
# Redis を使用する場合
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Flask-Caching を使用
pip install Flask-Caching redis
```

### CDN の設定（CloudFlare）
1. CloudFlare に登録
2. DNS レコードをポイント
3. 以下のキャッシュルールを設定：
   - `/static/*` → キャッシュ 30日
   - `/api/*` → キャッシュなし

## セキュリティ チェックリスト

- [ ] `.env` ファイルは Git に含めない
- [ ] HTTPS を有効化（Let's Encrypt）
- [ ] SQL インジェクション対策（Flask は ORM で対策済み）
- [ ] CSRF トークン設定（Flask-WTF）
- [ ] レート制限を実装
- [ ] ログ監視とアラート設定
- [ ] 定期的なセキュリティ更新
- [ ] API キーローテーション計画

## バックアップ戦略

### cache ディレクトリのバックアップ
```bash
# 毎日 00:00 にバックアップ（cron）
0 0 * * * tar -czf /backup/market-reports-$(date +\%Y\%m\%d).tar.gz /opt/market-reports/cache/

# AWS S3 にアップロード
0 1 * * * aws s3 cp /backup/market-reports-*.tar.gz s3://your-backup-bucket/
```

## トラブルシューティング

### ポート 5000 が既に使用されている
```bash
# プロセスを確認
sudo lsof -i :5000

# 別のポートで起動
gunicorn -b 0.0.0.0:8000 app:app
```

### メモリ使用量が多い場合
```bash
# ワーカー数を削減
gunicorn -w 2 -b 0.0.0.0:5000 app:app

# メモリ制限を設定
gunicorn -w 4 --max-requests 1000 app:app
```

### API タイムアウト
```python
# app.py で設定
gunicorn --timeout 180 app:app
```

## 本番環境チェックリスト

- [ ] 環境変数が正しく設定されている
- [ ] API キーが有効期限内である
- [ ] データベース接続がテストされた
- [ ] ログローテーション設定
- [ ] バックアップが動作している
- [ ] モニタリングダッシュボードが構成されている
- [ ] アラートが設定されている
- [ ] 障害復旧計画（RTO/RPO）が定義されている
