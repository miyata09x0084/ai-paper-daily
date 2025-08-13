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
        # AI関連のキーワードで検索クエリを作成
        ai_categories = [
            "cs.AI",  # Artificial Intelligence
            "cs.LG",  # Machine Learning  
            "cs.CL",  # Computation and Language
            "cs.CV",  # Computer Vision
            "cs.NE",  # Neural and Evolutionary Computing
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
    
    def filter_important_papers(self, papers: List[Dict], min_importance_keywords: int = 2) -> List[Dict]:
        """
        重要そうな論文をフィルタリング
        
        Args:
            papers: 論文リスト
            min_importance_keywords: 重要キーワードの最小出現数
        
        Returns:
            フィルタリング後の論文リスト
        """
        importance_keywords = [
            "transformer", "attention", "llm", "large language model", 
            "gpt", "bert", "diffusion", "generative", "multimodal",
            "reinforcement learning", "deep learning", "neural network",
            "computer vision", "natural language processing", "nlp",
            "few-shot", "zero-shot", "in-context learning", "fine-tuning",
            "benchmark", "sota", "state-of-the-art", "breakthrough"
        ]
        
        filtered_papers = []
        
        for paper in papers:
            text_to_check = (paper["title"] + " " + paper["summary"]).lower()
            keyword_count = sum(1 for keyword in importance_keywords if keyword in text_to_check)
            
            if keyword_count >= min_importance_keywords:
                paper["importance_score"] = keyword_count
                filtered_papers.append(paper)
        
        # 重要度スコアでソート
        filtered_papers.sort(key=lambda x: x["importance_score"], reverse=True)
        
        return filtered_papers