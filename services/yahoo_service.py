"""
Yahoo Finance Service for sector performance data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class YahooFinanceService:
    SECTOR_ETFS = {
        'XLK': {'name': 'Technology', 'ja_name': 'テクノロジー'},
        'XLF': {'name': 'Financials', 'ja_name': '金融'},
        'XLE': {'name': 'Energy', 'ja_name': 'エネルギー'},
        'XLV': {'name': 'Healthcare', 'ja_name': 'ヘルスケア'},
        'XLY': {'name': 'Consumer Discretionary', 'ja_name': '裁量消費'},
        'XLP': {'name': 'Consumer Staples', 'ja_name': '必需消費'},
        'XLU': {'name': 'Utilities', 'ja_name': 'ユーティリティ'},
        'XLI': {'name': 'Industrials', 'ja_name': '産業'},
        'XLB': {'name': 'Materials', 'ja_name': '素材'},
        'XLRE': {'name': 'Real Estate', 'ja_name': '不動産'},
        'XLC': {'name': 'Communication', 'ja_name': '通信'},
    }

    def get_sector_performance(self):
        results = []
        today = datetime.now()
        year_start = datetime(today.year, 1, 1)

        for ticker, info in self.SECTOR_ETFS.items():
            try:
                etf = yf.Ticker(ticker)
                hist = etf.history(start=year_start - timedelta(days=35), end=today)

                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]
                ytd_start_price = hist['Close'].iloc[0]

                # 1週間前
                week_ago_idx = max(0, len(hist) - 6)
                week_ago_price = hist['Close'].iloc[week_ago_idx]

                # 1ヶ月前
                month_ago_idx = max(0, len(hist) - 22)
                month_ago_price = hist['Close'].iloc[month_ago_idx]

                ytd_return = ((current_price - ytd_start_price) / ytd_start_price) * 100
                weekly_return = ((current_price - week_ago_price) / week_ago_price) * 100
                monthly_return = ((current_price - month_ago_price) / month_ago_price) * 100

                results.append({
                    'ticker': ticker,
                    'name': info['name'],
                    'ja_name': info['ja_name'],
                    'current_price': round(current_price, 2),
                    'ytd_start_price': round(ytd_start_price, 2),
                    'week_ago_price': round(week_ago_price, 2),
                    'month_ago_price': round(month_ago_price, 2),
                    'ytd': round(ytd_return, 2),
                    'weekly': round(weekly_return, 2),
                    'monthly': round(monthly_return, 2),
                })

            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

        results.sort(key=lambda x: x['ytd'], reverse=True)
        return results