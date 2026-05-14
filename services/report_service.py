"""
Weekly Report Generation Service
"""
from datetime import datetime
import os
from anthropic import Anthropic

class ReportService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"

    def generate_weekly_report(self, macro_data, geo_data, sector_data, language='en'):
        """Generate a full weekly report combining all data sources"""
        
        # Prepare sector summary
        sectors = sector_data.get('sectors', [])
        top3 = sectors[:3] if sectors else []
        sector_text = '\n'.join([
            f"- {s.get('name', '')}: YTD {s.get('ytd', 0):.1f}%"
            for s in top3
        ]) if top3 else 'N/A'

        # Prepare geo summary
        geo_summary = geo_data.get('summary', geo_data.get('summary_ja', 'N/A'))

        if language == 'ja':
            prompt = f"""あなたは機関投資家向けの週次マーケットレポートを執筆するプロのアナリストです。
以下のデータをもとに、長期投資家向けの週次レポートを日本語で作成してください。

【マクロ経済データ】
FF金利: {macro_data.get('FF_RATE', 'N/A')}%
CPI: {macro_data.get('CPI', 'N/A')}%
GDP成長率: {macro_data.get('GDP', 'N/A')}%
失業率: {macro_data.get('UNEMPLOYMENT', 'N/A')}%

【地政学リスク概要】
{geo_summary}

【セクターパフォーマンス上位3】
{sector_text}

以下の構成で作成してください：
1. 今週のマーケットサマリー（3-4文）
2. マクロ経済の注目ポイント（2-3個）
3. 地政学リスクと市場への影響（2-3文）
4. セクター動向と注目セクター（2-3文）
5. 長期投資家へのインプリケーション（3-4文）

Markdownの**太字**や##見出しは使わず、プレーンテキストで作成してください。各セクションは番号と見出しで区切ってください。"""

        else:
            prompt = f"""You are a professional analyst writing a weekly market report for institutional investors.
Based on the following data, create a weekly report for long-term investors.

[MACRO ECONOMIC DATA]
Fed Funds Rate: {macro_data.get('FF_RATE', 'N/A')}%
CPI: {macro_data.get('CPI', 'N/A')}%
GDP Growth: {macro_data.get('GDP', 'N/A')}%
Unemployment Rate: {macro_data.get('UNEMPLOYMENT', 'N/A')}%

[GEOPOLITICAL RISK SUMMARY]
{geo_summary}

[TOP 3 SECTOR PERFORMANCE]
{sector_text}

Structure your report as follows:
1. Weekly Market Summary (3-4 sentences)
2. Macro Economic Highlights (2-3 points)
3. Geopolitical Risk & Market Impact (2-3 sentences)
4. Sector Trends & Key Sectors to Watch (2-3 sentences)
5. Implications for Long-term Investors (3-4 sentences)

Use plain text only. Separate each section with its number and title."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating report: {str(e)}"

    def get_report_metadata(self):
        """Get report metadata for the current week"""
        now = datetime.now()
        week_num = now.isocalendar()[1]
        return {
            'week': week_num,
            'year': now.year,
            'generated_at': now.isoformat(),
            'title_en': f'Weekly Market Report — Week {week_num}, {now.year}',
            'title_ja': f'週次マーケットレポート — {now.year}年第{week_num}週'
        }