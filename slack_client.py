import requests
import json
from typing import List
import os


class SlackClient:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        
    def send_message(self, text: str, channel: str = None) -> bool:
        """
        Slackにメッセージを送信する
        
        Args:
            text: 送信するテキスト
            channel: 送信先チャンネル（Webhookで設定済みの場合は不要）
            
        Returns:
            送信成功の可否
        """
        if not self.webhook_url:
            print("Error: Slack webhook URL is not configured")
            return False
            
        payload = {
            "text": text,
            "mrkdwn": True  # Markdownフォーマットを有効にする
        }
        
        if channel:
            payload["channel"] = channel
            
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                print("Slack message sent successfully")
                return True
            else:
                print(f"Failed to send Slack message: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"Error sending Slack message: {e}")
            return False
    
    def send_paper_summaries(self, summaries: List[str]) -> bool:
        """
        論文要約を分割して送信する（Slackの文字数制限対応）
        
        Args:
            summaries: 要約リスト
            
        Returns:
            送信成功の可否
        """
        if not summaries:
            print("No summaries to send")
            return False
            
        # メッセージをチャンクに分割（Slackの4000文字制限を考慮）
        max_chunk_size = 3500  # 余裕を持って設定
        
        current_chunk = ""
        chunks = []
        
        for summary in summaries:
            # 現在のチャンクに追加可能かチェック
            if len(current_chunk) + len(summary) + 2 < max_chunk_size:  # +2 for newlines
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += summary
            else:
                # 現在のチャンクを保存し、新しいチャンクを開始
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = summary
        
        # 最後のチャンクを追加
        if current_chunk:
            chunks.append(current_chunk)
        
        # 各チャンクを送信
        all_success = True
        for i, chunk in enumerate(chunks):
            if len(chunks) > 1:
                # 複数チャンクの場合は番号を付ける
                chunk_text = f"*📊 AI論文日報 ({i+1}/{len(chunks)})*\n\n{chunk}"
            else:
                chunk_text = chunk
                
            success = self.send_message(chunk_text)
            if not success:
                all_success = False
                
        return all_success
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        エラー通知を送信する
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            送信成功の可否
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_text = f"""🚨 **AI論文日報システム エラー**

**時刻:** {timestamp}
**エラー:** {error_message}

システム管理者に確認をお願いします。
"""
        
        return self.send_message(error_text)
    
    def send_test_message(self) -> bool:
        """
        テストメッセージを送信する
        
        Returns:
            送信成功の可否
        """
        test_text = """🧪 **AI論文日報システム テスト**

システムが正常に動作しています！
毎日最新のAI研究をお届けします。

*このメッセージはテスト送信です*
"""
        
        return self.send_message(test_text)