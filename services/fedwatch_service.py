"""
Fed Rate Probability Calculator using FF Futures
"""
import requests
from datetime import datetime

class FedWatchService:
    
    FOMC_MEETINGS = [
        {'date': '2026-06-17', 'label': '2026/06/17'},
        {'date': '2026-07-28', 'label': '2026/07/28'},
        {'date': '2026-09-15', 'label': '2026/09/15'},
        {'date': '2026-10-27', 'label': '2026/10/27'},
        {'date': '2026-12-09', 'label': '2026/12/09'},
        {'date': '2027-01-27', 'label': '2027/01/27'},
        {'date': '2027-03-17', 'label': '2027/03/17'},
        {'date': '2027-04-28', 'label': '2027/04/28'},
        {'date': '2027-06-09', 'label': '2027/06/09'},
        {'date': '2027-07-28', 'label': '2027/07/28'},
        {'date': '2027-09-15', 'label': '2027/09/15'},
    ]
    
    FUTURES_TICKERS = {
        '2026-06': 'ZQM26.CBT',
        '2026-07': 'ZQN26.CBT',
        '2026-08': 'ZQQ26.CBT',
        '2026-09': 'ZQU26.CBT',
        '2026-10': 'ZQV26.CBT',
        '2026-11': 'ZQX26.CBT',
        '2026-12': 'ZQZ26.CBT',
        '2027-01': 'ZQF27.CBT',
        '2027-02': 'ZQG27.CBT',
        '2027-03': 'ZQH27.CBT',
        '2027-04': 'ZQJ27.CBT',
        '2027-05': 'ZQK27.CBT',
        '2027-06': 'ZQM27.CBT',
        '2027-07': 'ZQN27.CBT',
        '2027-08': 'ZQQ27.CBT',
        '2027-09': 'ZQU27.CBT',
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
        # Generate rate ranges (in basis points, converted to %)
        # Current rate 4.33 -> range 425-450 (rounded to nearest 25bp)
        base = round(current_rate * 4) / 4  # round to nearest 0.25
        
        # Generate ranges from -200bp to +50bp of current
        ranges = []
        r = base - 2.00
        while r <= base + 0.25:
            low = round(r * 100)
            high = low + 25
            ranges.append({
                'label': f'{low}-{high}',
                'low': r,
                'high': r + 0.25
            })
            r = round(r + 0.25, 2)

        results = []
        prev_implied = current_rate

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

            # Calculate probability for each range
            # Using simple linear interpolation between ranges
            probs = {}
            for rng in ranges:
                diff = implied_rate - (rng['low'] + 0.125)  # midpoint
                prob = max(0, 100 - abs(diff) / 0.25 * 100)
                probs[rng['label']] = round(prob, 2)

            # Normalize to 100%
            total = sum(probs.values())
            if total > 0:
                for key in probs:
                    probs[key] = round(probs[key] / total * 100, 2)

            results.append({
                'date': meeting['label'],
                'implied_rate': implied_rate,
                'rate_diff': round(current_rate - implied_rate, 3),
                'cumulative_cuts': round((current_rate - implied_rate) / 0.25, 2),
                'probabilities': probs
            })

            prev_implied = implied_rate

        return {'ranges': [r['label'] for r in ranges], 'meetings': results}