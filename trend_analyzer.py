from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import re
from datetime import datetime, timedelta


class TrendAnalyzer:
    def __init__(self):
        # Webエンジニア向けのトレンドキーワード
        self.trend_keywords = {
            # AI/ML技術トレンド
            "ai_ml": [
                "llm", "large language model", "gpt", "transformer", "attention",
                "diffusion", "generative ai", "foundation model", "multimodal",
                "retrieval augmented generation", "rag", "fine-tuning", "rlhf",
                "chain of thought", "in-context learning", "few-shot", "zero-shot"
            ],
            # 開発技術トレンド
            "development": [
                "code generation", "copilot", "coding assistant", "automated testing",
                "ci/cd", "devops", "microservices", "serverless", "containerization",
                "kubernetes", "api", "rest", "graphql", "websocket", "real-time"
            ],
            # Web技術トレンド
            "web_tech": [
                "react", "vue", "angular", "svelte", "nextjs", "nuxt", "remix",
                "typescript", "javascript", "node.js", "deno", "bun",
                "tailwind", "css", "html", "pwa", "spa", "ssr", "ssg"
            ],
            # データ・インフラトレンド
            "data_infra": [
                "database", "nosql", "sql", "postgresql", "mongodb", "redis",
                "elasticsearch", "vector database", "embedding", "search",
                "caching", "cdn", "cloud", "aws", "azure", "gcp", "edge computing"
            ],
            # セキュリティトレンド
            "security": [
                "security", "authentication", "authorization", "oauth", "jwt",
                "encryption", "vulnerability", "privacy", "gdpr", "compliance",
                "zero trust", "devsecops", "penetration testing", "threat detection"
            ],
            # パフォーマンス・監視トレンド
            "performance": [
                "performance", "optimization", "monitoring", "observability",
                "metrics", "logging", "tracing", "alerting", "sli", "slo",
                "load balancing", "scalability", "high availability", "latency"
            ]
        }
        
        # 新興技術キーワード（高重要度）
        self.emerging_keywords = [
            "webassembly", "wasm", "web3", "blockchain", "metaverse", "ar", "vr",
            "quantum computing", "edge ai", "federated learning", "mlops",
            "chatops", "gitops", "platform engineering", "developer experience"
        ]
    
    def extract_trends(self, papers: List[Dict], days_back: int = 7) -> Dict:
        """
        論文データからトレンド情報を抽出
        
        Args:
            papers: 論文リスト
            days_back: 比較対象とする日数
            
        Returns:
            トレンド分析結果
        """
        # キーワード出現頻度をカウント
        category_counts = defaultdict(Counter)
        keyword_counts = Counter()
        emerging_counts = Counter()
        
        # 著者所属機関カウント
        institution_counts = Counter()
        
        # 研究分野カテゴリカウント
        arxiv_category_counts = Counter()
        
        for paper in papers:
            text = (paper["title"] + " " + paper["summary"]).lower()
            
            # カテゴリ別キーワードをカウント
            for category, keywords in self.trend_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        category_counts[category][keyword] += 1
                        keyword_counts[keyword] += 1
            
            # 新興技術キーワードをカウント
            for keyword in self.emerging_keywords:
                if keyword in text:
                    emerging_counts[keyword] += 1
            
            # 著者所属機関を抽出
            for author in paper.get("authors", []):
                # 簡単な機関名抽出（@以降があれば）
                author_lower = author.lower()
                institutions = ["google", "meta", "microsoft", "amazon", "openai", "anthropic",
                              "stanford", "mit", "berkeley", "harvard", "carnegie mellon"]
                for inst in institutions:
                    if inst in author_lower:
                        institution_counts[inst] += 1
                        break
            
            # ArXivカテゴリをカウント
            for category in paper.get("categories", []):
                arxiv_category_counts[category] += 1
        
        return {
            "category_trends": dict(category_counts),
            "top_keywords": keyword_counts.most_common(10),
            "emerging_tech": emerging_counts.most_common(5),
            "active_institutions": institution_counts.most_common(5),
            "research_areas": arxiv_category_counts.most_common(8),
            "total_papers": len(papers)
        }
    
    def generate_trend_summary(self, trends: Dict) -> str:
        """
        トレンド分析結果から要約テキストを生成
        """
        summary_parts = []
        
        # 全体統計
        summary_parts.append(f"📊 **今日の研究動向** (対象: {trends['total_papers']}件の論文)")
        summary_parts.append("")
        
        # トップキーワード
        if trends["top_keywords"]:
            summary_parts.append("🔥 **注目キーワード TOP5:**")
            for i, (keyword, count) in enumerate(trends["top_keywords"][:5], 1):
                summary_parts.append(f"  {i}. **{keyword.title()}** ({count}件)")
        
        summary_parts.append("")
        
        # カテゴリ別トレンド
        category_names = {
            "ai_ml": "🤖 AI/ML技術",
            "development": "⚙️ 開発技術", 
            "web_tech": "🌐 Web技術",
            "data_infra": "💾 データ・インフラ",
            "security": "🔒 セキュリティ",
            "performance": "⚡ パフォーマンス"
        }
        
        summary_parts.append("📈 **分野別トレンド:**")
        for category, name in category_names.items():
            if category in trends["category_trends"] and trends["category_trends"][category]:
                top_keyword = trends["category_trends"][category].most_common(1)[0]
                total_count = sum(trends["category_trends"][category].values())
                summary_parts.append(f"  {name}: **{top_keyword[0].title()}** ({total_count}件)")
        
        summary_parts.append("")
        
        # 新興技術
        if trends["emerging_tech"]:
            summary_parts.append("🚀 **新興技術動向:**")
            for keyword, count in trends["emerging_tech"]:
                summary_parts.append(f"  • **{keyword.title()}** ({count}件)")
            summary_parts.append("")
        
        # アクティブな研究機関
        if trends["active_institutions"]:
            summary_parts.append("🏛️ **活発な研究機関:**")
            for inst, count in trends["active_institutions"]:
                summary_parts.append(f"  • **{inst.title()}** ({count}件)")
            summary_parts.append("")
        
        # 研究分野
        if trends["research_areas"]:
            summary_parts.append("📚 **活発な研究分野:**")
            area_names = {
                "cs.AI": "人工知能", "cs.LG": "機械学習", "cs.CL": "自然言語処理",
                "cs.SE": "ソフトウェア工学", "cs.HC": "HCI", "cs.IR": "情報検索",
                "cs.DB": "データベース", "cs.DC": "分散システム", "cs.PL": "プログラミング言語",
                "cs.CR": "暗号・セキュリティ", "cs.CV": "コンピュータビジョン"
            }
            for area, count in trends["research_areas"][:5]:
                display_name = area_names.get(area, area)
                summary_parts.append(f"  • **{display_name}** ({count}件)")
        
        return "\n".join(summary_parts)
    
    def detect_trend_changes(self, current_papers: List[Dict], 
                           historical_papers: List[Dict] = None) -> str:
        """
        トレンドの変化を検出（将来の拡張用）
        """
        if not historical_papers:
            return "📅 **トレンド変化**: データ不足のため比較分析は次回から利用可能です"
        
        current_trends = self.extract_trends(current_papers)
        historical_trends = self.extract_trends(historical_papers)
        
        # 簡単な増減分析
        changes = []
        for keyword, count in current_trends["top_keywords"][:5]:
            # 過去データでの出現回数を検索
            historical_count = 0
            for hist_keyword, hist_count in historical_trends["top_keywords"]:
                if hist_keyword == keyword:
                    historical_count = hist_count
                    break
            
            if historical_count == 0:
                changes.append(f"  🆕 **{keyword.title()}** (新登場)")
            elif count > historical_count:
                changes.append(f"  📈 **{keyword.title()}** (+{count - historical_count}件)")
            elif count < historical_count:
                changes.append(f"  📉 **{keyword.title()}** (-{historical_count - count}件)")
        
        if changes:
            return "📅 **トレンド変化:**\n" + "\n".join(changes)
        else:
            return "📅 **トレンド変化**: 大きな変動は見られません"