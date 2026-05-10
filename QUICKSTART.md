# Quick Start Guide - Market Reports Dashboard

投資家向けダッシュボードを5分で起動するための手順です。

## 📋 前提条件

- Python 3.8 以上
- pip (Python パッケージ管理ツール)
- インターネット接続

## 🔑 必要な API キー

以下のサービスから API キーを取得してください（無料）：

1. **Claude API** (Anthropic)
   - https://console.anthropic.com
   - Sign up → API Keys → Create API Key

2. **FRED API** (Federal Reserve)
   - https://fredaccount.stlouisfed.org/login
   - Register → Request API Key (無料)

3. **NewsAPI**
   - https://newsapi.org
   - Sign up → API Key を取得

## 🚀 5ステップで起動

### ステップ 1: セットアップスクリプトを実行

#### Windows:
```bash
setup.bat
```

#### macOS/Linux:
```bash
bash setup.sh
```

### ステップ 2: 環境変数を設定

`.env` ファイルを編集して、API キーを設定：

```bash
# テキストエディタで .env を開く
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
FRED_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
NEWSAPI_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
FLASK_ENV=development
SECRET_KEY=your_secure_secret_key
```

### ステップ 3: 仮想環境を有効化

#### Windows:
```bash
venv\Scripts\activate
```

#### macOS/Linux:
```bash
source venv/bin/activate
```

### ステップ 4: アプリケーションを起動

```bash
python app.py
```

出力例：
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### ステップ 5: ブラウザで開く

ブラウザで以下にアクセス：
```
http://localhost:5000
```

## ✅ 動作確認

以下が正しく表示されたら成功です：

- ✅ **Macro Overview**: FF金利、CPI、GDP、失業率が表示
- ✅ **Geopolitical Radar**: 地政学ニュースと AI 要約が表示
- ✅ **Sector Scorecard**: セクター別パフォーマンスがランキング表示
- ✅ **言語切替**: ページ右上の日本語ボタンで日本語に切り替わる

## 🎨 ダッシュボードの主な機能

### 1. リアルタイムデータ更新
- マクロ経済指標は 30 分ごとに自動更新
- 🔄 **Refresh** ボタンで手動更新も可能

### 2. AI 分析コメント
- Claude AI が経済指標を分析して週次コメント生成
- 地政学リスクの投資家向け要約を自動作成

### 3. マルチ言語対応
- 右上のボタンで English ↔ 日本語 を切り替え
- すべてのテキストが自動翻訳

### 4. セクター比較
- YTD（年初来）、1ヶ月、1週間のパフォーマンスを表示
- タブをクリックして期間を変更

## 📊 データソース

| セクション | データソース | 更新頻度 |
|-----------|----------|--------|
| Macro Overview | FRED API | 30分 |
| Geopolitical Radar | NewsAPI | 30分 |
| Sector Scorecard | Yahoo Finance | 30分 |

## 🛠️ よくあるエラーと解決方法

### API キーエラー
```
Error: CLAUDE_API_KEY not found
```
→ `.env` ファイルが正しく設定されているか確認

### ポート 5000 が既に使用されている
```
Address already in use
```
→ 別のターミナルで以下を実行：
```bash
python app.py --port 8000
```

### インターネット接続エラー
```
Error fetching data...
```
→ API サービスが稼働しているか確認（status.anthropic.com など）

### モジュールが見つからない
```
ModuleNotFoundError: No module named 'anthropic'
```
→ 仮想環境が有効になっているか確認：
```bash
pip install -r requirements.txt
```

## 📱 モバイルでの表示確認

LAN 内の他のデバイスからアクセス：

1. ホスト PC の IP アドレスを確認：
   ```bash
   # Windows
   ipconfig
   
   # macOS/Linux
   ifconfig
   ```

2. 他のデバイスで以下にアクセス：
   ```
   http://YOUR_IP:5000
   ```

## 🔒 本番環境への展開

Docker を使用した簡単なデプロイ：

```bash
# イメージをビルド
docker build -t market-reports .

# コンテナを実行
docker run -d \
  --name market-reports \
  -p 80:5000 \
  --env-file .env \
  market-reports

# または Docker Compose を使用
docker-compose up -d
```

詳細は [DEPLOYMENT.md](DEPLOYMENT.md) を参照。

## 📚 次のステップ

### ドキュメントを読む
- [README.md](README.md) - プロジェクト概要と詳細設定
- [API.md](API.md) - API エンドポイント仕様
- [DEPLOYMENT.md](DEPLOYMENT.md) - 本番環境へのデプロイ方法

### カスタマイズ
- セクター ETF を変更する: [services/yahoo_service.py](services/yahoo_service.py#L7)
- カラースキームを変更する: [static/css/style.css](static/css/style.css#L10)
- 更新間隔を変更する: [config.py](config.py#L24)

### 開発
```bash
# デバッグモード
FLASK_ENV=development python app.py

# コードを変更すると自動リロード
# ブラウザで http://localhost:5000 をリフレッシュ
```

## 🐛 バグ報告とサポート

問題が発生した場合：

1. ターミナルのエラーメッセージを確認
2. API キーが有効か確認
3. ネットワーク接続を確認
4. キャッシュをクリア：
   ```bash
   rm -rf cache/*  # Linux/macOS
   rmdir /s cache  # Windows
   ```
5. アプリケーションを再起動

## 📞 サポートリソース

- Claude API ドキュメント: https://docs.anthropic.com
- FRED API ドキュメント: https://fredaccount.stlouisfed.org/api
- NewsAPI ドキュメント: https://newsapi.org/docs
- Flask ドキュメント: https://flask.palletsprojects.com

## 🎯 次の機能アップデート予定

- [ ] PostgreSQL データベース統合
- [ ] ユーザーアカウント機能
- [ ] カスタムアラート設定
- [ ] ポートフォリオ追跡機能
- [ ] GraphQL API サポート
- [ ] 機械学習による予測分析

---

**🎉 セットアップ完了！Happy investing!**
