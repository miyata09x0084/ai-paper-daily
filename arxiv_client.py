import requests
import feedparser
from datetime import datetime, timedelta
import pytz
from typing import List, Dict


class ArxivClient:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        
    def fetch_recent_ai_papers(self, days_back: int = 1, max_results: int = 20) -> List[Dict]:
        """
        最近のAI関連論文を取得する
        
        Args:
            days_back: 何日前までの論文を取得するか
            max_results: 最大取得件数
        
        Returns:
            論文情報のリスト
        """
        # Webエンジニアに関連する研究分野で検索クエリを作成
        ai_categories = [
            "cs.AI",  # Artificial Intelligence
            "cs.LG",  # Machine Learning  
            "cs.CL",  # Computation and Language
            "cs.SE",  # Software Engineering
            "cs.HC",  # Human-Computer Interaction
            "cs.IR",  # Information Retrieval
            "cs.DB",  # Databases
            "cs.DC",  # Distributed Computing
            "cs.PL",  # Programming Languages
            "cs.CR",  # Cryptography and Security
        ]
        
        # カテゴリークエリを構築
        category_query = " OR ".join([f"cat:{cat}" for cat in ai_categories])
        
        # 日付範囲を設定
        end_date = datetime.now(pytz.UTC)
        start_date = end_date - timedelta(days=days_back)
        
        # ArXiv APIのクエリパラメータ
        params = {
            "search_query": f"({category_query}) AND submittedDate:[{start_date.strftime('%Y%m%d')}* TO {end_date.strftime('%Y%m%d')}*]",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            papers = []
            
            for entry in feed.entries:
                paper = {
                    "id": entry.id.split("/")[-1],
                    "title": entry.title.strip().replace('\n', ' '),
                    "summary": entry.summary.strip().replace('\n', ' '),
                    "authors": [author.name for author in entry.authors],
                    "published": entry.published,
                    "updated": entry.updated if hasattr(entry, 'updated') else entry.published,
                    "categories": [tag.term for tag in entry.tags],
                    "link": entry.link,
                    "pdf_link": next((link.href for link in entry.links if link.type == 'application/pdf'), None)
                }
                papers.append(paper)
                
            return papers
            
        except requests.RequestException as e:
            print(f"ArXiv API request failed: {e}")
            return []
        except Exception as e:
            print(f"Error parsing ArXiv response: {e}")
            return []
    
    def filter_important_papers(self, papers: List[Dict], min_importance_score: float = 5.0) -> List[Dict]:
        """
        重要そうな論文をフィルタリング（多層評価システム）
        
        Args:
            papers: 論文リスト
            min_importance_score: 重要度スコアの最小閾値
        
        Returns:
            フィルタリング後の論文リスト
        """
        # 高優先度キーワード（重み3.0） - Webエンジニア向け実用的AI技術
        high_priority_keywords = [
            "code generation", "code completion", "copilot", "coding assistant",
            "web development", "frontend", "backend", "full stack",
            "automated testing", "test generation", "bug detection", "code review",
            "deployment", "devops", "ci/cd", "continuous integration",
            "api", "rest", "graphql", "microservices", "serverless",
            "javascript", "typescript", "react", "vue", "angular", "node.js",
            "python", "django", "flask", "fastapi",
            "web security", "vulnerability detection", "security analysis"
        ]
        
        # 中優先度キーワード（重み2.0） - AI技術の実用応用
        medium_priority_keywords = [
            "llm", "large language model", "gpt", "claude", "gemini",
            "retrieval augmented generation", "rag", "embeddings", "vector database",
            "chatbot", "conversational ai", "customer support", "virtual assistant",
            "search", "recommendation", "personalization", "content generation",
            "natural language processing", "nlp", "text analysis", "sentiment analysis",
            "automated workflow", "process automation", "intelligent agent",
            "real-time", "streaming", "scalability", "performance optimization",
            "user experience", "ux", "accessibility", "personalization"
        ]
        
        # 基本キーワード（重み1.0） - 基礎技術・品質関連
        basic_keywords = [
            "machine learning", "deep learning", "neural network",
            "optimization", "efficient", "lightweight", "fast", "low latency",
            "monitoring", "observability", "analytics", "metrics",
            "database", "caching", "storage", "data processing",
            "cloud", "aws", "azure", "gcp", "kubernetes", "docker",
            "performance", "benchmark", "evaluation", "testing",
            "maintainability", "reliability", "robustness"
        ]
        
        # 除外キーワード（これらがあると重要度を下げる）
        exclusion_keywords = [
            "survey", "review", "tutorial", "preliminary", "work in progress",
            "short paper", "position paper", "demo", "poster",
            "theoretical", "mathematical proof", "formal verification",
            "robotics", "hardware", "embedded", "iot sensor",
            "medical", "healthcare", "biology", "physics", "chemistry"
        ]
        
        # 権威ある機関・企業（Webエンジニア観点）
        prestigious_affiliations = [
            "google", "meta", "microsoft", "amazon", "netflix", "uber", "airbnb",
            "github", "openai", "anthropic", "vercel", "stripe", "shopify",
            "stanford", "mit", "berkeley", "carnegie mellon", "toronto",
            "deepmind", "hugging face", "databricks", "snowflake"
        ]
        
        filtered_papers = []
        
        for paper in papers:
            title_lower = paper["title"].lower()
            summary_lower = paper["summary"].lower()
            authors_lower = " ".join(paper["authors"]).lower()
            text_to_check = title_lower + " " + summary_lower
            
            # 基本スコア計算
            score = 0.0
            
            # 高優先度キーワードチェック
            for keyword in high_priority_keywords:
                if keyword in text_to_check:
                    score += 3.0
                    # タイトルに含まれる場合はさらにボーナス
                    if keyword in title_lower:
                        score += 1.0
            
            # 中優先度キーワードチェック
            for keyword in medium_priority_keywords:
                if keyword in text_to_check:
                    score += 2.0
                    if keyword in title_lower:
                        score += 0.5
            
            # 基本キーワードチェック
            for keyword in basic_keywords:
                if keyword in text_to_check:
                    score += 1.0
            
            # 権威ある機関ボーナス
            for affiliation in prestigious_affiliations:
                if affiliation in authors_lower:
                    score += 2.0
                    break
            
            # 除外キーワードペナルティ
            for keyword in exclusion_keywords:
                if keyword in text_to_check:
                    score -= 2.0
            
            # 実用性指標によるボーナス・ペナルティ
            
            # 実装・実用性キーワードボーナス
            practical_keywords = [
                "implementation", "system", "framework", "tool", "platform",
                "open source", "github", "repository", "dataset", "benchmark",
                "evaluation", "experiment", "comparison", "analysis", "study"
            ]
            for keyword in practical_keywords:
                if keyword in text_to_check:
                    score += 1.5
            
            # カテゴリーによるボーナス（Webエンジニア関連分野）
            web_relevant_categories = ["cs.SE", "cs.HC", "cs.IR", "cs.DB", "cs.DC", "cs.PL", "cs.CR"]
            for category in paper["categories"]:
                if category in web_relevant_categories:
                    score += 2.0
                    break
            
            # 著者数によるボーナス（適度な共同研究＝実用性の高い研究傾向）
            if 2 <= len(paper["authors"]) <= 6:  # Webエンジニア向けは小規模チーム重視
                score += 1.0
            elif len(paper["authors"]) > 12:  # 著者が多すぎる場合はペナルティ
                score -= 1.0
            
            # 最近性ボーナス（より新しい技術を重視）
            from datetime import datetime
            try:
                pub_date = datetime.strptime(paper["published"][:10], "%Y-%m-%d")
                days_old = (datetime.now() - pub_date).days
                if days_old <= 30:  # 1ヶ月以内
                    score += 1.0
                elif days_old <= 90:  # 3ヶ月以内
                    score += 0.5
            except:
                pass  # 日付解析エラーは無視
            
            # 最終スコアが閾値を超える場合のみ採用
            if score >= min_importance_score:
                paper["importance_score"] = round(score, 2)
                filtered_papers.append(paper)
        
        # 重要度スコアでソート
        filtered_papers.sort(key=lambda x: x["importance_score"], reverse=True)
        
        return filtered_papers