# API Documentation - Market Reports Dashboard

## ベース URL
```
http://localhost:5000
```

本番環境では `https://your_domain.com` に置き換えてください。

## 認証

現在、パブリック API です。本番環境では API キーまたは JWT トークンベースの認証を追加することを推奨します。

## レスポンス形式

すべてのレスポンスは JSON 形式です。

### 成功レスポンス例
```json
{
    "status": "success",
    "data": {}
}
```

### エラーレスポンス例
```json
{
    "error": "Error message",
    "status": 400
}
```

## エンドポイント

### 1. ダッシュボード全体データ取得

#### リクエスト
```http
GET /api/dashboard?language=en
```

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| language | string | `en` (English) または `ja` (日本語) |

#### レスポンス例
```json
{
    "macro_overview": {
        "data": {
            "FF_RATE": 5.33,
            "CPI": 3.2,
            "GDP": 1.5,
            "UNEMPLOYMENT": 3.8
        },
        "commentary": "The Federal Reserve...",
        "commentary_ja": "連邦準備制度..."
    },
    "geopolitical_radar": {
        "news": [...],
        "summary": "Current geopolitical risks...",
        "summary_ja": "現在の地政学的リスク..."
    },
    "sector_scorecard": {
        "sectors": [...]
    }
}
```

#### HTTP ステータスコード
- `200` OK
- `500` Internal Server Error

---

### 2. マクロ概況データ取得

#### リクエスト
```http
GET /api/macro-overview?language=en
```

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| language | string | `en` または `ja` |

#### レスポンス例
```json
{
    "data": {
        "FF_RATE": 5.33,
        "FF_RATE_date": "2024-05-01",
        "CPI": 3.2,
        "CPI_date": "2024-04-01",
        "GDP": 1.5,
        "GDP_date": "2024-01-01",
        "UNEMPLOYMENT": 3.8,
        "UNEMPLOYMENT_date": "2024-04-01"
    },
    "commentary": "Weekly market commentary from Claude AI...",
    "commentary_ja": "Claude AI からの週次コメント..."
}
```

#### フィールド説明
- `FF_RATE`: Federal Funds Rate (%)
- `CPI`: Consumer Price Index (YoY %)
- `GDP`: GDP Growth Rate (%)
- `UNEMPLOYMENT`: Unemployment Rate (%)
- `commentary`: 英語版 AI コメント
- `commentary_ja`: 日本語版 AI コメント

#### HTTP ステータスコード
- `200` OK
- `500` Internal Server Error

---

### 3. 地政学レーダーデータ取得

#### リクエスト
```http
GET /api/geopolitical-radar?language=en
```

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| language | string | `en` または `ja` |

#### レスポンス例
```json
{
    "news": [
        {
            "title": "Geopolitical tensions escalate...",
            "description": "New sanctions...",
            "url": "https://example.com/article",
            "source": "Reuters",
            "publishedAt": "2024-05-01T12:00:00Z",
            "image": "https://example.com/image.jpg"
        }
    ],
    "summary": "Risk assessment from Claude AI...",
    "summary_ja": "Claude AI によるリスク評価..."
}
```

#### フィールド説明
- `news`: ニュース記事配列
  - `title`: 記事タイトル
  - `description`: 記事要約
  - `url`: 元記事へのリンク
  - `source`: ニュースソース
  - `publishedAt`: 公開日時（ISO 8601形式）
  - `image`: 記事画像 URL
- `summary`: 英語版 AI リスク評価
- `summary_ja`: 日本語版 AI リスク評価

#### HTTP ステータスコード
- `200` OK
- `500` Internal Server Error

---

### 4. セクタースコアカード取得

#### リクエスト
```http
GET /api/sector-scorecard?language=en
```

#### パラメータ
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| language | string | `en` または `ja` |

#### レスポンス例
```json
{
    "sectors": [
        {
            "ticker": "XLK",
            "name": "Technology",
            "ja_name": "テクノロジー",
            "current_price": 175.45,
            "ytd_return": 12.50,
            "monthly_return": 3.20,
            "weekly_return": 1.10,
            "updated_at": "2024-05-01T15:00:00"
        },
        {
            "ticker": "XLF",
            "name": "Financials",
            "ja_name": "金融",
            "current_price": 98.30,
            "ytd_return": 5.20,
            "monthly_return": 1.80,
            "weekly_return": 0.50,
            "updated_at": "2024-05-01T15:00:00"
        }
    ]
}
```

#### フィールド説明
- `ticker`: ETF ティッカー
- `name`: 英語セクター名
- `ja_name`: 日本語セクター名
- `current_price`: 現在価格（$）
- `ytd_return`: 年初来リターン（%）
- `monthly_return`: 1ヶ月リターン（%）
- `weekly_return`: 1週間リターン（%）
- `updated_at`: 更新日時（ISO 8601形式）

#### HTTP ステータスコード
- `200` OK
- `500` Internal Server Error

---

### 5. データ手動更新

#### リクエスト
```http
POST /api/refresh
Content-Type: application/json
```

#### リクエストボディ
なし（空の POST）

#### レスポンス例
```json
{
    "status": "success",
    "message": "Data refreshed"
}
```

#### HTTP ステータスコード
- `200` OK
- `500` Internal Server Error

#### 説明
すべてのダッシュボード データを即座に更新します。キャッシュをバイパスして新しいデータを取得します。

---

### 6. ヘルスチェック

#### リクエスト
```http
GET /api/health
```

#### レスポンス例
```json
{
    "status": "healthy",
    "has_macro": true,
    "has_geo": true,
    "has_sectors": true
}
```

#### レスポンスフィールド
- `status`: サービスステータス（`healthy` または `unhealthy`）
- `has_macro`: マクロデータ取得可否
- `has_geo`: 地政学データ取得可否
- `has_sectors`: セクターデータ取得可否

#### HTTP ステータスコード
- `200` OK

#### 説明
バックエンドの稼働状態確認用。ロードバランサーなどの監視用途で使用できます。

---

## エラーハンドリング

### HTTP エラーコード

| コード | 説明 |
|--------|------|
| `200` | 成功 |
| `400` | 不正なリクエスト |
| `404` | リソースが見つからない |
| `500` | サーバー内部エラー |

### エラーレスポンス例
```json
{
    "error": "No data available",
    "status": 500
}
```

---

## レート制限（推奨）

本番環境での API レート制限設定例：

```python
# Flask-Limiter を使用
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/dashboard')
@limiter.limit("10 per minute")
def get_dashboard():
    pass
```

---

## キャッシング情報

### デフォルトキャッシュ TTL

| エンドポイント | TTL | 説明 |
|--------------|-----|------|
| `/api/dashboard` | 1時間 | すべてのデータキャッシュ |
| `/api/macro-overview` | 1時間 | マクロデータキャッシュ |
| `/api/geopolitical-radar` | 1時間 | ニュースデータキャッシュ |
| `/api/sector-scorecard` | 1時間 | セクターデータキャッシュ |
| `/api/refresh` | なし | キャッシュをバイパス |
| `/api/health` | なし | リアルタイム確認 |

### キャッシュ制御ヘッダー
```
Cache-Control: public, max-age=3600
Last-Modified: <timestamp>
ETag: <hash>
```

---

## CORS 設定

現在、CORS は有効です。本番環境では以下のように制限することを推奨：

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your_domain.com"],
        "methods": ["GET", "POST"],
        "max_age": 3600
    }
})
```

---

## Webhook 実装例

データ更新時に外部システムに通知する場合：

```python
import requests

def send_webhook(event_type, data):
    webhook_url = os.getenv('WEBHOOK_URL')
    payload = {
        'event': event_type,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
```

---

## GraphQL API（将来対応予定）

GraphQL スキーマの実装準備：

```graphql
type Query {
    macroOverview(language: String!): MacroOverview
    geopoliticalRadar(language: String!): GeopoliticalRadar
    sectorScorecard(language: String!): [Sector]
    health: HealthStatus
}

type MacroOverview {
    ffRate: Float
    cpi: Float
    gdp: Float
    unemployment: Float
    commentary: String
    updatedAt: DateTime
}

type Sector {
    ticker: String!
    name: String!
    currentPrice: Float!
    ytdReturn: Float!
    monthlyReturn: Float!
    weeklyReturn: Float!
}
```

---

## SDK/Client Library

### Python クライアント例
```python
import requests

class MarketReportsClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_dashboard(self, language="en"):
        return self.session.get(
            f"{self.base_url}/api/dashboard",
            params={"language": language}
        ).json()
    
    def get_macro_overview(self, language="en"):
        return self.session.get(
            f"{self.base_url}/api/macro-overview",
            params={"language": language}
        ).json()
    
    def refresh_data(self):
        return self.session.post(
            f"{self.base_url}/api/refresh"
        ).json()

# 使用例
client = MarketReportsClient()
dashboard = client.get_dashboard(language="ja")
print(dashboard['macro_overview'])
```

### JavaScript クライアント例
```javascript
class MarketReportsClient {
    constructor(baseUrl = "http://localhost:5000") {
        this.baseUrl = baseUrl;
    }
    
    async getDashboard(language = "en") {
        const response = await fetch(
            `${this.baseUrl}/api/dashboard?language=${language}`
        );
        return response.json();
    }
    
    async getMacroOverview(language = "en") {
        const response = await fetch(
            `${this.baseUrl}/api/macro-overview?language=${language}`
        );
        return response.json();
    }
    
    async refreshData() {
        const response = await fetch(
            `${this.baseUrl}/api/refresh`,
            { method: "POST" }
        );
        return response.json();
    }
}

// 使用例
const client = new MarketReportsClient();
const dashboard = await client.getDashboard("ja");
console.log(dashboard.macro_overview);
```

---

## ログレベルと監視

### ログフォーマット
```
[%(asctime)s] %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]
```

### 監視対象メトリクス
- API レスポンスタイム
- エラー率
- API 呼び出し数（FRED、NewsAPI、Yahoo Finance）
- キャッシュ ヒット率
- メモリ使用量
- CPU 使用率

---

## テスト

### cURL を使用したテスト例
```bash
# ダッシュボード全体
curl "http://localhost:5000/api/dashboard?language=en"

# マクロ概況
curl "http://localhost:5000/api/macro-overview?language=ja"

# 地政学レーダー
curl "http://localhost:5000/api/geopolitical-radar"

# セクタースコアカード
curl "http://localhost:5000/api/sector-scorecard"

# データ更新
curl -X POST "http://localhost:5000/api/refresh"

# ヘルスチェック
curl "http://localhost:5000/api/health"
```

### Python を使用したテスト例
```python
import requests
import json

base_url = "http://localhost:5000"

# テスト
response = requests.get(f"{base_url}/api/health")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
```

---

## バージョニング

現在のバージョン: `v1.0.0`

将来的に API バージョニングを実装する場合：
```
GET /api/v1/dashboard
GET /api/v2/dashboard  # 新しいバージョン
```

---

## 質問 & サポート

API に関する問題は GitHub Issues で報告してください。
