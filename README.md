# Market Reports Dashboard

投資家向けのリアルタイムマーケットダッシュボード。Flask + Python + Claude APIで構築。

## 機能

### 📈 Macro Overview
- **FF金利（Federal Funds Rate）**: リアルタイムの政策金利
- **CPI（消費者物価指数）**: インフレ指標
- **GDP成長率**: 経済成長トレンド
- **失業率**: 雇用市場状況
- **AI分析**: Claude AIが週次コメント自動生成

### ⚠️ Geopolitical Radar
- **地政学リスク検出**: NewsAPIから自動取得
- **投資家向け要約**: Claude AIが市場への影響を分析
- **トレンドニュース**: 最新の地政学リスク関連ニュース表示

### 🏆 Sector Scorecard
- **セクター別パフォーマンス**: XLK, XLF, XLE, XLV, XLY, XLP, XLU, XLI, XLB, VOT
- **複数期間表示**: YTD, 1ヶ月, 1週間のリターン
- **ランキング表示**: パフォーマンス順のランキング

## デザイン
- **ピンク系カラーパレット**: Earnings Analyzerと同じ高級感あるピンク系
- **レスポンシブデザイン**: デスクトップ、タブレット、モバイル対応
- **ダークモード**: 目に優しいダークテーマ

## 言語対応
- 🇬🇧 English / 🇯🇵 日本語 - ワンクリック切替可能

## 必要な API キー

### 1. Claude API Key
- [Anthropic Claude API](https://console.anthropic.com)から取得
- `CLAUDE_API_KEY` に設定

### 2. FRED API Key
- [Federal Reserve Economic Data](https://fredaccount.stlouisfed.org/login)から取得
- 無料登録で取得可能
- `FRED_API_KEY` に設定

### 3. NewsAPI Key
- [NewsAPI](https://newsapi.org)から取得
- `NEWSAPI_KEY` に設定

## インストール

### 1. リポジトリをクローン
```bash
cd MarketReports
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# または
source venv/bin/activate      # macOS/Linux
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
`.env` ファイルを編集してAPIキーを設定：
```
CLAUDE_API_KEY=your_claude_api_key_here
FRED_API_KEY=your_fred_api_key_here
NEWSAPI_KEY=your_newsapi_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=5000
```

## 実行方法

### 開発環境での起動
```bash
python app.py
```

ブラウザで http://localhost:5000 にアクセス

### 本番環境での起動
```bash
FLASK_ENV=production python app.py
```

または Gunicorn を使用：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## プロジェクト構造

```
MarketReports/
├── app.py                 # メイン Flask アプリケーション
├── config.py              # 設定ファイル
├── requirements.txt       # Python 依存パッケージ
├── .env                   # 環境変数（Git管理外）
├── .gitignore             # Git無視設定
│
├── services/              # データ取得サービス
│   ├── __init__.py
│   ├── fred_service.py    # FRED API 統合
│   ├── newsapi_service.py # NewsAPI 統合
│   ├── yahoo_service.py   # Yahoo Finance 統合
│   └── claude_service.py  # Claude AI 統合
│
├── utils/                 # ユーティリティ
│   ├── __init__.py
│   ├── cache.py           # キャッシング機能
│   └── scheduler.py       # 定期更新スケジューラー
│
├── static/                # 静的ファイル
│   ├── css/
│   │   └── style.css      # ピンク系スタイルシート
│   ├── js/
│   │   ├── main.js        # メイン機能
│   │   └── translation.js # 言語切替機能
│   └── img/               # 画像ディレクトリ
│
├── templates/             # HTML テンプレート
│   └── index.html         # メインダッシュボード
│
└── cache/                 # データキャッシュ（自動生成）
```

## 主要機能

### 自動更新スケジューリング
- デフォルト: 30分毎に自動更新
- `config.py` の `UPDATE_INTERVAL` で変更可能
- バックグラウンドで非同期実行

### キャッシング
- 1時間単位でデータキャッシュ
- API呼び出し削減でコスト最適化
- `config.py` の `CACHE_TTL` で変更可能

### AI分析
- Claude AIが経済指標をリアルタイム分析
- 週次マクロコメント自動生成
- 地政学リスク要約の自動作成
- 多言語対応（英語・日本語）

## カスタマイズ

### 更新間隔の変更
`config.py`:
```python
UPDATE_INTERVAL = 15  # 15分毎に更新
```

### キャッシュTTLの変更
`config.py`:
```python
CACHE_TTL = 1800  # 30分
```

### セクター ETF の追加/変更
`services/yahoo_service.py` の `SECTOR_ETFS` を編集：
```python
SECTOR_ETFS = {
    'XLK': {'name': 'Technology', 'ja_name': 'テクノロジー'},
    # 新しい ETF を追加
    'YOUR_TICKER': {'name': 'Name', 'ja_name': '日本語名'},
}
```

### カラースキームの変更
`static/css/style.css` の CSS変数を編集：
```css
:root {
    --primary-pink: #FF6B9D;
    /* その他の色を変更 */
}
```

## トラブルシューティング

### APIキーエラー
- `.env` ファイルが正しく設定されているか確認
- APIキーに有効期限がないか確認
- API サービスが稼働しているか確認

### キャッシュクリア
```bash
# Python スクリプトで実行
from utils.cache import CacheManager
cache = CacheManager()
cache.clear()
```

### ログ確認
```bash
# Flask ログを確認
python app.py  # ターミナルに詳細ログが表示
```

## パフォーマンス最適化

- **キャッシング**: データベースキャッシュで API 呼び出し削減
- **非同期更新**: バックグラウンドスケジューラーで UI ブロッキング回避
- **圧縮**: CSS/JS の本番環境での圧縮推奨

## セキュリティ注意事項

1. **本番環境での設定**:
   - `FLASK_ENV=production` に設定
   - `SECRET_KEY` を強力なランダム文字列に変更
   - HTTPS を有効化

2. **API キー管理**:
   - `.env` は絶対に Git にコミットしない
   - 環境変数として設定推奨
   - 定期的にキーをローテーション

3. **CORS 設定**:
   - 必要に応じて CORS ホワイトリストを設定

## ライセンス

このプロジェクトはMITライセンス下で公開されています。

## 使用技術

- **Backend**: Flask 3.0.0
- **Language**: Python 3.8+
- **AI**: Anthropic Claude API
- **Data Sources**: 
  - FRED API (Federal Reserve Economic Data)
  - NewsAPI
  - Yahoo Finance
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Scheduling**: APScheduler
- **Caching**: JSON ファイルベース

## 開発者向け情報

### API エンドポイント

- `GET /api/dashboard` - ダッシュボード全体データ
- `GET /api/macro-overview` - マクロ概況データ
- `GET /api/geopolitical-radar` - 地政学レーダーデータ
- `GET /api/sector-scorecard` - セクタースコアカードデータ
- `POST /api/refresh` - 手動データ更新
- `GET /api/health` - ヘルスチェック

### クエリパラメータ

言語指定:
```
?language=en  # 英語
?language=ja  # 日本語（デフォルト）
```

## サポート

問題が発生した場合：
1. ログを確認
2. API キーが有効か確認
3. ネットワーク接続を確認
4. キャッシュをクリアして再実行
