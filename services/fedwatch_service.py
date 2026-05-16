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
        results = []
        increment = 0.25

        future_meetings = []
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
            future_meetings.append({
                'meeting': meeting,
                'ticker': ticker,
                'price': price,
                'implied_rate': implied_rate,
                'meeting_date': meeting_date
            })

        n = len(future_meetings)
        if n == 0:
            return []

        # 最終会合のimplied_rateから総カット数を計算
        final_implied = future_meetings[-1]['implied_rate']
        total_cuts_expected = (current_rate - final_implied) / increment  # 例：2.24回

        for i, m in enumerate(future_meetings):
            implied_rate = m['implied_rate']
            # この会合までの累積カット期待値
            cumulative_cuts = (current_rate - implied_rate) / increment
            # 前回会合までの累積カット期待値
            if i == 0:
                prev_cuts = 0
            else:
                prev_implied = future_meetings[i-1]['implied_rate']
                prev_cuts = (current_rate - prev_implied) / increment

            # この会合での追加カット期待値
            marginal_cut = cumulative_cuts - prev_cuts

            # 確率に変換（0〜1回の間を線形補間）
            prob_cut = round(min(max(marginal_cut * 100, 0), 100), 1)
            prob_hold = round(100 - prob_cut, 1)
            prob_hike = 0

            results.append({
                'date': m['meeting']['date'],
                'label': m['meeting']['label'],
                'implied_rate': implied_rate,
                'prob_cut': prob_cut,
                'prob_hold': prob_hold,
                'prob_hike': prob_hike,
                'ticker': m['ticker'],
                'futures_price': m['price']
            })

        return results