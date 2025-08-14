# AI論文日報システム

arxivからAI関連の重要な新着論文を自動取得し、ChatGPT APIで要約を生成してSlackに毎日投稿するシステムです。

## 🌟 主な機能

- **自動論文収集**: arxiv APIからAI関連の最新論文を取得
- **インテリジェント選別**: 重要キーワードベースで論文をフィルタリング
- **日本語要約生成**: ChatGPT APIを使用した分かりやすい論文要約
- **Slack自動投稿**: 要約をSlackチャンネルに自動配信
- **エラー処理**: 問題発生時の通知機能

## 📋 必要な準備

### 1. APIキーとWebhook URLの取得

#### OpenAI API
1. [OpenAI Platform](https://platform.openai.com/)でアカウント作成
2. API キーを生成
3. 使用料金の設定（従量課金）

#### Slack Webhook
1. [Slack API](https://api.slack.com/apps)で新しいアプリを作成
2. "Incoming Webhooks"機能を有効化
3. 投稿したいチャンネル用のWebhook URLを生成

### 2. Python環境の準備

```bash
# Python 3.8以上が必要
python --version

# 仮想環境の作成（推奨）
python -m venv ai-paper-env
source ai-paper-env/bin/activate  # Windowsの場合: ai-paper-env\\Scripts\\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

⚠️ **重要**: 実際のAPI キーやWebhook URLは絶対にGitリポジトリにコミットしないでください。

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集してAPI情報を設定
vi .env
```

`.env`ファイルの設定例：
```env
# OpenAI Platform（https://platform.openai.com/）で取得
OPENAI_API_KEY=実際のOpenAI_APIキーをここに入力

# Slack App設定で生成されたWebhook URLをここに入力
SLACK_WEBHOOK_URL=実際のSlack_Webhook_URLをここに入力
```

💡 **セキュリティのポイント**:
- `.env`ファイルは`.gitignore`で除外済み
- 実際の値はプレースホルダーと置き換えて使用
- API キーは定期的にローテーションすることを推奨

## 🚀 使い方

### システムテスト
```bash
# Slack接続テスト
python main.py test
```

### 通常実行
```bash
# 論文日報を生成・送信
python main.py
```

### 実行可能にする
```bash
# スクリプトを実行可能にする
chmod +x main.py

# 直接実行
./main.py
```

## ⏰ 自動実行の設定

### cron（macOS/Linux）
```bash
# crontabを編集
crontab -e

# 毎日朝9時に実行する例
0 9 * * * cd /path/to/ai-paper-daily && /path/to/python main.py >> /var/log/ai-paper-daily.log 2>&1
```

### systemd（Linux）
```bash
# サービスファイルを作成
sudo vi /etc/systemd/system/ai-paper-daily.service

# タイマーファイルを作成
sudo vi /etc/systemd/system/ai-paper-daily.timer

# サービスを有効化
sudo systemctl enable ai-paper-daily.timer
sudo systemctl start ai-paper-daily.timer
```

### GitHub Actions
```yaml
# .github/workflows/daily-papers.yml
name: Daily AI Papers
on:
  schedule:
    - cron: '0 0 * * *'  # 毎日00:00 UTC
  workflow_dispatch:

jobs:
  send-papers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run script
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python main.py
```

## 🛠 設定のカスタマイズ

### 論文取得条件の調整

`main.py`の以下の部分を変更：

```python
# 取得日数を変更（デフォルト: 1日）
papers = arxiv_client.fetch_recent_ai_papers(days_back=2, max_results=50)

# 要約する論文数を変更（デフォルト: 5件）
top_papers = important_papers[:10]
```

### 重要キーワードの追加

`arxiv_client.py`の`filter_important_papers`メソッドで重要キーワードを追加：

```python
importance_keywords = [
    "transformer", "attention", "llm", "large language model",
    # 新しいキーワードを追加
    "rag", "retrieval augmented generation", "moe", "mixture of experts",
]
```

### 要約フォーマットの変更

`openai_client.py`の`summarize_paper`メソッドでプロンプトをカスタマイズできます。

## 📊 出力例

システムが生成するSlackメッセージの例：

```
🤖 AI論文日報 - 2024年1月15日

今日の注目AI論文をお届けします！

---

📄 Attention Is All You Need: Revisited

🎯 何を解決する研究か:
従来のRNNやCNNに代わる、より効率的な系列変換モデルの開発

💡 提案手法の要点:
完全にattention機構のみに基づくTransformerアーキテクチャを提案
エンコーダー・デコーダー構造でself-attentionとmulti-head attentionを活用

📊 結果・成果:
機械翻訳タスクでSOTA達成、訓練時間も大幅短縮

🚀 なぜ重要か:
現在の大規模言語モデルの基盤となる革新的アーキテクチャ

📎 論文リンク: https://arxiv.org/abs/1706.03762

---
🔬 このレポートは最新のAI研究動向をお届けする自動配信です
📧 ご質問・ご要望がございましたらお気軽にお声かけください
```

## 🔧 トラブルシューティング

### よくあるエラー

1. **OpenAI API エラー**
   - API キーの確認
   - 利用料金の確認
   - レート制限の確認

2. **Slack投稿エラー**
   - Webhook URLの確認
   - チャンネル権限の確認
   - メッセージサイズの確認

3. **arxiv接続エラー**
   - ネットワーク接続の確認
   - API制限の確認
   - プロキシ設定の確認

### ログの確認

```bash
# エラーログの表示
python main.py 2>&1 | tee ai-paper-daily.log
```

## 🤝 貢献

バグ報告や機能改善の提案はIssueまでお願いします。

## 📄 ライセンス

MIT License

## 🙏 謝辞

- [arxiv API](https://arxiv.org/help/api/)
- [OpenAI API](https://platform.openai.com/)
- [Slack API](https://api.slack.com/)