#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from arxiv_client import ArxivClient
from openai_client import OpenAIClient
from slack_client import SlackClient
from trend_analyzer import TrendAnalyzer


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
        trend_analyzer = TrendAnalyzer()
        
        print("📚 ArXivから最新のAI論文を取得中...")
        
        # ArXivから最新の論文を取得（重要論文が少ない場合に備えて多めに取得）
        papers = arxiv_client.fetch_recent_ai_papers(days_back=1, max_results=100)
        
        if not papers:
            print("⚠️  論文が見つかりませんでした")
            slack_client.send_error_notification("論文の取得に失敗しました")
            return False
        
        print(f"✅ {len(papers)}件の論文を取得しました")
        
        # 重要な論文をフィルタリング（厳格な基準：スコア5.0以上）
        important_papers = arxiv_client.filter_important_papers(papers, min_importance_score=5.0)
        
        # デバッグ情報：上位10件のスコア表示
        if important_papers:
            print("🏆 重要度トップ論文のスコア:")
            for i, paper in enumerate(important_papers[:10], 1):
                print(f"  {i}. スコア {paper['importance_score']}: {paper['title'][:80]}...")
        
        # 重要論文が少なすぎる場合は基準を緩める
        if len(important_papers) < 3:
            print("⚠️  厳格基準では重要論文が少なすぎます。基準を緩めて再検索...")
            important_papers = arxiv_client.filter_important_papers(papers, min_importance_score=3.0)
            print(f"🔍 緩和基準で{len(important_papers)}件の重要論文を選出")
        
        if not important_papers:
            print("⚠️  重要な論文が見つかりませんでした")
            # 最低限、基本キーワードでフィルタリング
            important_papers = arxiv_client.filter_important_papers(papers, min_importance_score=1.0)[:5]
            if important_papers:
                print(f"📋 最低基準で{len(important_papers)}件の論文を選出")
            else:
                slack_client.send_error_notification("重要な論文が見つかりませんでした")
                return False
            
        print(f"🔍 最終的に{len(important_papers)}件の重要論文を選出しました")
        
        # 上位論文を要約（最大3件に限定してより質を重視）
        top_papers = important_papers[:3]
        print(f"📝 上位{len(top_papers)}件の論文を要約中...")
        
        summaries = openai_client.summarize_multiple_papers(top_papers)
        
        if not summaries:
            print("❌ 要約の生成に失敗しました")
            slack_client.send_error_notification("論文要約の生成に失敗しました")
            return False
        
        print(f"✅ {len(summaries)}件の要約を生成しました")
        
        # トレンド分析を実行
        print("📊 トレンド分析を実行中...")
        trends = trend_analyzer.extract_trends(papers)  # 全論文からトレンド抽出
        trend_summary = trend_analyzer.generate_trend_summary(trends)
        
        # 日次要約メッセージを作成（トレンド情報を含む）
        daily_summary = openai_client.create_daily_summary(summaries)
        combined_message = daily_summary + "\n\n---\n\n" + trend_summary
        
        # Slackに送信
        print("📤 Slackに送信中...")
        success = slack_client.send_message(combined_message)
        
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