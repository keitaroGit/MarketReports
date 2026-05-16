"""
Fed Rate Probability Calculator using FF Futures
"""
import requests
from datetime import datetime, timedelta

class FedWatchService:
    
    # FOMC meeting dates 2025-2026
    FOMC_MEETINGS = [
        {'date': '2026-06-17', 'label': 'Jun 2026'},
        {'date': '2026-07-28', 'label': 'Jul 2026'},
        {'date': '2026-09-15', 'label': 'Sep 2026'},
        {'date': '2026-10-27', 'label': 'Oct 2026'},
        {'date': '2026-12-15', 'label': 'Dec 2026'},
    ]
    
    # FF Futures ticker mapping (month -> ZQ ticker)
    FUTURES_TICKERS = {
        '2025-06': 'ZQM25.CBT',
        '2025-07': 'ZQN25.CBT',
        '2025-08': 'ZQQ25.CBT',
        '2025-09': 'ZQU25.CBT',
        '2025-10': 'ZQV25.CBT',
        '2025-11': 'ZQX25.CBT',
        '2025-12': 'ZQZ25.CBT',
        '2026-01': 'ZQF26.CBT',
        '2026-02': 'ZQG26.CBT',
        '2026-03': 'ZQH26.CBT',
        '2026-04': 'ZQJ26.CBT',
        '2026-05': 'ZQK26.CBT',
        '2026-06': 'ZQM26.CBT',
	    '2026-07': 'ZQN26.CBT',
        '2026-08': 'ZQQ26.CBT',
        '2026-09': 'ZQU26.CBT',
        '2026-10': 'ZQV26.CBT',
        '2026-11': 'ZQX26.CBT',
        '2026-12': 'ZQZ26.CBT',
    }

    def get_futures_price(self, ticker):
        """Get FF futures price from Yahoo Finance"""
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = data['chart']['result'][0]['meta']['regularMarketPrice']
                return price
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
        return None

    def calculate_probabilities(self, current_rate=4.33):
        """Calculate rate change probabilities for each FOMC meeting"""
        results = []
        increment = 0.25
        prev_implied_rate = current_rate  # 前回会合後のレートとして使う

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

            # この会合での変化幅（前回比）
            rate_diff = prev_implied_rate - implied_rate

            if rate_diff >= increment * 0.75:
                prob_cut = min(round((rate_diff / increment) * 100, 1), 100)
                prob_hold = round(100 - prob_cut, 1)
                prob_hike = 0
            elif rate_diff <= -increment * 0.75:
                prob_hike = min(round((-rate_diff / increment) * 100, 1), 100)
                prob_hold = round(100 - prob_hike, 1)
                prob_cut = 0
            else:
                prob_cut = round((rate_diff / increment) * 100, 1)
                prob_hike = 0
                prob_hold = round(100 - abs(prob_cut), 1)
                prob_cut = max(0, prob_cut)

            results.append({
                'date': meeting['date'],
                'label': meeting['label'],
                'implied_rate': implied_rate,
                'prob_cut': max(0, min(100, prob_cut)),
                'prob_hold': max(0, min(100, prob_hold)),
                'prob_hike': max(0, min(100, prob_hike)),
                'ticker': ticker,
                'futures_price': price
            })

            prev_implied_rate = implied_rate  # 次の会合の基準に

        return results