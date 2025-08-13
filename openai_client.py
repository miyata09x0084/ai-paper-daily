import openai
from typing import List, Dict
import os


class OpenAIClient:
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv('OPENAI_API_KEY')
        )
        
    def summarize_paper(self, paper: Dict) -> str:
        """
        論文を要約する
        
        Args:
            paper: 論文データ
            
        Returns:
            要約テキスト
        """
        prompt = f"""
以下のAI論文について、日本語で分かりやすく要約してください。
技術的な内容も含めて、以下の観点で整理してください：

タイトル: {paper['title']}
著者: {', '.join(paper['authors'][:3])}{'他' if len(paper['authors']) > 3 else ''}
カテゴリ: {', '.join(paper['categories'])}

アブストラクト:
{paper['summary']}

要約は以下の形式でお願いします：
**📄 {paper['title']}**

**🎯 何を解決する研究か:**
（研究の目的・問題設定を1-2行で）

**💡 提案手法の要点:**
（主要なアイデア・手法を2-3行で）

**📊 結果・成果:**
（実験結果や性能向上を1-2行で）

**🚀 なぜ重要か:**
（この研究の意義・インパクトを1-2行で）

**📎 論文リンク:** {paper['link']}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたはAI研究の専門家です。論文を分かりやすく要約し、その重要性を伝える専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._create_fallback_summary(paper)
    
    def _create_fallback_summary(self, paper: Dict) -> str:
        """
        API呼び出しに失敗した場合のフォールバック要約
        """
        authors_text = ', '.join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors_text += '他'
            
        return f"""**📄 {paper['title']}**

**👥 著者:** {authors_text}
**🏷 カテゴリ:** {', '.join(paper['categories'])}

**📝 概要:**
{paper['summary'][:500]}{'...' if len(paper['summary']) > 500 else ''}

**📎 論文リンク:** {paper['link']}

*（要約生成に失敗したため、元のアブストラクトを表示しています）*
"""

    def summarize_multiple_papers(self, papers: List[Dict], max_papers: int = 5) -> List[str]:
        """
        複数の論文を要約する
        
        Args:
            papers: 論文リスト
            max_papers: 要約する最大論文数
            
        Returns:
            要約テキストのリスト
        """
        summaries = []
        
        for i, paper in enumerate(papers[:max_papers]):
            print(f"要約生成中... ({i+1}/{min(len(papers), max_papers)})")
            summary = self.summarize_paper(paper)
            summaries.append(summary)
            
        return summaries
    
    def create_daily_summary(self, summaries: List[str]) -> str:
        """
        日次要約メッセージを作成する
        """
        from datetime import datetime
        
        today = datetime.now().strftime("%Y年%m月%d日")
        
        header = f"""🤖 **AI論文日報 - {today}**

今日の注目AI論文をお届けします！

---

"""
        
        footer = """
---
🔬 *このレポートは最新のAI研究動向をお届けする自動配信です*
📧 *ご質問・ご要望がございましたらお気軽にお声かけください*
"""
        
        return header + "\n\n".join(summaries) + "\n" + footer