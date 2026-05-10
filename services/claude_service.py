"""
Claude API Service for AI-powered analysis
"""
import os
from anthropic import Anthropic

class ClaudeService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"
    
    def generate_macro_commentary(self, macro_data, language='en'):
        if language == 'ja':
            prompt = f"""あなたは経験豊富な投資ストラテジストです。以下の最新マクロ経済指標を分析し、投資家向けの週次コメントを日本語で生成してください。タイトルや見出しは不要です。直接内容から始めてください。

FF金利: {macro_data.get('FF_RATE', 'N/A')}%
CPI（消費者物価指数）: {macro_data.get('CPI', 'N/A')}%
GDP成長率: {macro_data.get('GDP', 'N/A')}%
失業率: {macro_data.get('UNEMPLOYMENT', 'N/A')}%

以下の構成で回答してください：
1. 現在の経済情勢の要約（2-3文）
2. 主要リスク要因（2-3個）
3. 投資への示唆（3-4個）

Markdownの**太字**や##見出しは使わず、プレーンテキストで簡潔にお答えください。"""
        else:
            prompt = f"""You are an experienced investment strategist. Analyze the following latest macroeconomic indicators and generate a weekly commentary for institutional investors. Do not include any title or heading. Start directly with the content.

Fed Funds Rate: {macro_data.get('FF_RATE', 'N/A')}%
CPI (Consumer Price Index): {macro_data.get('CPI', 'N/A')}%
GDP Growth: {macro_data.get('GDP', 'N/A')}%
Unemployment Rate: {macro_data.get('UNEMPLOYMENT', 'N/A')}%

Structure your response as follows:
1. Current Economic Summary (2-3 sentences)
2. Key Risk Factors (2-3 items)
3. Investment Implications (3-4 key points)

Use plain text only, no Markdown formatting. Be concise and professional."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating commentary: {str(e)}"
    
    def generate_geopolitical_summary(self, news_items, language='en'):
        news_text = "\n".join([
            f"- {item.get('title', '')}: {item.get('description', '')[:100]}"
            for item in news_items[:5]
        ])
        
        if language == 'ja':
            prompt = f"""あなたは地政学リスク分析の専門家です。以下の最新地政学ニュースを分析し、投資家向けのリスク要約を日本語で生成してください。

【最新ニュース】
{news_text if news_text.strip() else "現在ニュースデータがありません。一般的な地政学リスクを分析してください。"}

以下の構成で回答してください：
1. 主要な地政学リスク要因（2-3個）
2. マーケットへの潜在的影響
3. 推奨される投資対応策

Markdownの**太字**や##見出しは使わず、プレーンテキストで簡潔にお答えください。"""
        else:
            prompt = f"""You are a geopolitical risk analyst. Analyze the following latest geopolitical news and generate a risk summary for investors.

Latest News:
{news_text if news_text.strip() else "No news data available. Please analyze general geopolitical risks."}

Structure your response as:
1. Key Geopolitical Risk Factors (2-3 items)
2. Potential Market Impact
3. Recommended Investment Response

Use plain text only, no Markdown formatting. Be concise and professional."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating summary: {str(e)}"