"""
Fed Rate Probability Calculator using FF Futures
"""
import requests
from datetime import datetime

class FedWatchService:
    
    FOMC_MEETINGS = [
        {'date': '2026-06-17', 'label': 'Jun 2026'},
        {'date': '2026-07-28', 'label': 'Jul 2026'},
        {'date': '2026-09-15', 'label': 'Sep 2026'},
        {'date': '2026-10-27', 'label': 'Oct 2026'},
        {'date': '2026-12-15', 'label': 'Dec 2026'},
    ]
    
    FUTURES_TICKERS = {
        '2026-06': 'ZQM26.CBT',
        '2026-07': 'ZQN26.CBT',
        '2026-08': 'ZQQ26.CBT',
        '2026-09': 'ZQU26.CBT',
        '2026-10': 'ZQV26.CBT',
        '2026-11': 'ZQX26.CBT',
        '2026-12': 'ZQZ26.CBT',
    }

    def get_futures_price(self, ticker):
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['chart']['result'][0]['meta']['regularMarketPrice']
        except Exception as e:
            print(f'Error fetching {ticker}: {e}')
        return None

    def calculate_probabilities(self, current_rate=4.33):
        results = []
        increment = 0.25
        for meeting in self.FOMC_MEETINGS:
            meeting_date = datetime.strptime(meeting['date'], '%Y-%m-%d')
            if meeting_date < datetime.now():
                continue
            month_key = meeting_date.strftime('%Y-%m')
            ticker = self.FUTURES_TICKERS.get(month_key)
            if not ticker:
                continue
            price = self.get_futures_price(ticker)
            if price is None:
                continue
            implied_rate = round(100 - price, 3)
            rate_diff = round(current_rate - implied_rate, 3)
            cumulative_cuts = round(rate_diff / increment, 2)
            results.append({
                'date': meeting['date'],
                'label': meeting['label'],
                'implied_rate': implied_rate,
                'rate_diff': rate_diff,
                'cumulative_cuts': cumulative_cuts,
                'ticker': ticker,
                'futures_price': price
            })
        return results