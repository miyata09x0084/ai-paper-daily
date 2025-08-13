#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from arxiv_client import ArxivClient
from openai_client import OpenAIClient
from slack_client import SlackClient


def main():
    """メイン実行関数"""
    print("🤖 AI論文日報システムを開始します...")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 環境変数をロード
    load_dotenv()
    
    # 必要な環境変数をチェック
    required_env_vars = ['OPENAI_API_KEY', 'SLACK_WEBHOOK_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"必要な環境変数が設定されていません: {', '.join(missing_vars)}"
        print(f"❌ {error_msg}")
        return False
    
    try:
        # 各クライアントを初期化
        arxiv_client = ArxivClient()
        openai_client = OpenAIClient()
        slack_client = SlackClient()
        
        print("📚 ArXivから最新のAI論文を取得中...")
        
        # ArXivから最新の論文を取得
        papers = arxiv_client.fetch_recent_ai_papers(days_back=1, max_results=50)
        
        if not papers:
            print("⚠️  論文が見つかりませんでした")
            slack_client.send_error_notification("論文の取得に失敗しました")
            return False
        
        print(f"✅ {len(papers)}件の論文を取得しました")
        
        # 重要な論文をフィルタリング
        important_papers = arxiv_client.filter_important_papers(papers, min_importance_keywords=1)
        
        if not important_papers:
            print("⚠️  重要な論文が見つかりませんでした")
            return False
            
        print(f"🔍 {len(important_papers)}件の重要論文を選出しました")
        
        # 上位論文を要約（最大5件）
        top_papers = important_papers[:5]
        print(f"📝 上位{len(top_papers)}件の論文を要約中...")
        
        summaries = openai_client.summarize_multiple_papers(top_papers)
        
        if not summaries:
            print("❌ 要約の生成に失敗しました")
            slack_client.send_error_notification("論文要約の生成に失敗しました")
            return False
        
        print(f"✅ {len(summaries)}件の要約を生成しました")
        
        # 日次要約メッセージを作成
        daily_summary = openai_client.create_daily_summary(summaries)
        
        # Slackに送信
        print("📤 Slackに送信中...")
        success = slack_client.send_message(daily_summary)
        
        if success:
            print("✅ Slackへの送信が完了しました！")
            return True
        else:
            print("❌ Slackへの送信に失敗しました")
            return False
            
    except Exception as e:
        error_msg = f"予期しないエラーが発生しました: {str(e)}"
        print(f"❌ {error_msg}")
        
        try:
            slack_client.send_error_notification(error_msg)
        except:
            pass  # エラー通知の送信にも失敗した場合は無視
            
        return False


def test_system():
    """システムのテスト実行"""
    print("🧪 システムテストを実行します...")
    
    # 環境変数をロード
    load_dotenv()
    
    # Slack接続テスト
    slack_client = SlackClient()
    success = slack_client.send_test_message()
    
    if success:
        print("✅ システムテスト完了！")
        return True
    else:
        print("❌ システムテストに失敗しました")
        return False


if __name__ == "__main__":
    # コマンドライン引数をチェック
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # テストモード
        success = test_system()
    else:
        # 通常実行
        success = main()
    
    # 終了コードを設定
    sys.exit(0 if success else 1)