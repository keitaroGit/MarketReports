"""
FRED API Service - Economic Calendar Data
"""
import os
import requests
from datetime import datetime, timedelta

class FREDService:
    BASE_URL = 'https://api.stlouisfed.org/fred'
    
    # FRED Series IDs for each indicator
    SERIES = {
        'CORE_PCE_MOM':   {'id': 'PCEPILFE',    'name': 'Core PCE Price Index MoM', 'name_ja': 'コアPCEデフレーター前月比', 'unit': '%', 'importance': 3, 'transform': 'pch'},
        'CORE_PCE_YOY':   {'id': 'PCEPILFE',    'name': 'Core PCE Price Index YoY', 'name_ja': 'コアPCEデフレーター前年比', 'unit': '%', 'importance': 3, 'transform': 'pc1'},
        'CPI_MOM':        {'id': 'CPIAUCSL',    'name': 'CPI MoM',                  'name_ja': 'CPI前月比',               'unit': '%', 'importance': 3, 'transform': 'pch'},
        'CPI_YOY':        {'id': 'CPIAUCSL',    'name': 'CPI YoY',                  'name_ja': 'CPI前年比',               'unit': '%', 'importance': 3, 'transform': 'pc1'},
        'PPI_MOM':        {'id': 'PPIACO',      'name': 'PPI MoM',                  'name_ja': 'PPI前月比',               'unit': '%', 'importance': 2, 'transform': 'pch'},
        'GDP':            {'id': 'A191RL1Q225SBEA', 'name': 'GDP QoQ',              'name_ja': 'GDP前期比年率',            'unit': '%', 'importance': 3, 'transform': 'lin'},
        'UNEMPLOYMENT':   {'id': 'UNRATE',      'name': 'Unemployment Rate',        'name_ja': '失業率',                  'unit': '%', 'importance': 3, 'transform': 'lin'},
        'NONFARM':        {'id': 'PAYEMS',      'name': 'Nonfarm Payrolls',         'name_ja': '非農業部門雇用者数',       'unit': 'K', 'importance': 3, 'transform': 'chg'},
        'JOBLESS_CLAIMS': {'id': 'ICSA',        'name': 'Initial Jobless Claims',   'name_ja': '新規失業保険申請件数',     'unit': 'K', 'importance': 2, 'transform': 'lin'},
    }

    DESCRIPTIONS = {
        'CORE_PCE_MOM': {
            'en': "The Fed's preferred inflation gauge, excluding food & energy. Above 0.2% keeps rate cut hopes in check.",
            'ja': "FRBが最重視するインフレ指標（食品・エネルギー除く）。0.2%超が続くと利下げ期待が後退。"
        },
        'CORE_PCE_YOY': {
            'en': "Year-over-year core PCE. The Fed targets 2%. Remaining above target limits room for rate cuts.",
            'ja': "コアPCEの前年比。FRBの目標は2%。目標を上回る状態が続くと利下げ余地を制限する。"
        },
        'CPI_MOM': {
            'en': "Monthly change in consumer prices. The primary inflation measure watched by markets and the Fed.",
            'ja': "消費者物価の前月比変化。市場とFRBが注目する主要インフレ指標。"
        },
        'CPI_YOY': {
            'en': "Year-over-year CPI. Measures broad inflation trends. Above 3% raises concerns about sticky inflation.",
            'ja': "CPIの前年比。インフレのトレンドを示す。3%超が続くと根強いインフレへの懸念が高まる。"
        },
        'PPI_MOM': {
            'en': "Monthly change in producer prices. A leading indicator of consumer inflation trends.",
            'ja': "生産者物価の前月比変化。消費者インフレの先行指標として注目される。"
        },
        'GDP': {
            'en': "Annualized quarterly GDP growth rate. Measures the pace of economic expansion or contraction.",
            'ja': "GDP前期比年率成長率。経済の拡大・縮小ペースを示す最重要指標。"
        },
        'UNEMPLOYMENT': {
            'en': "Percentage of the labor force that is unemployed. Rising rate signals labor market softening.",
            'ja': "労働力人口に占める失業者の割合。上昇は労働市場の軟化を示す。"
        },
        'NONFARM': {
            'en': "Monthly change in US jobs excluding farming. The most watched labor market report. Drives major market moves.",
            'ja': "農業部門を除く米国の月次雇用者数変化。最も注目される雇用指標。発表後に大きな相場変動が起きやすい。"
        },
        'JOBLESS_CLAIMS': {
            'en': "Weekly count of new unemployment benefit filings. Lower = stronger labor market.",
            'ja': "週次の新規失業保険申請件数。低いほど労働市場が堅調。"
        },
    }

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('FRED_API_KEY')

    def get_series(self, series_id, transform='lin', limit=3):
        """Fetch latest observations from FRED"""
        try:
            url = f'{self.BASE_URL}/series/observations'
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': limit,
                'units': transform
            }
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                obs = res.json().get('observations', [])
                valid = [o for o in obs if o['value'] != '.']
                return valid
        except Exception as e:
            print(f"FRED error {series_id}: {e}")
        return []

    def get_release_dates(self, series_id):
        """Get next release date for a series"""
        try:
            url = f'{self.BASE_URL}/series/release'
            params = {'series_id': series_id, 'api_key': self.api_key, 'file_type': 'json'}
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                release_id = res.json()['releases'][0]['id']
                url2 = f'{self.BASE_URL}/release/dates'
                params2 = {'release_id': release_id, 'api_key': self.api_key, 'file_type': 'json', 'sort_order': 'desc', 'limit': 5}
                res2 = requests.get(url2, params=params2, timeout=10)
                if res2.status_code == 200:
                    return res2.json().get('release_dates', [])
        except Exception as e:
            print(f"FRED release date error {series_id}: {e}")
        return []

    def get_calendar_data(self):
        """Build calendar events from FRED data"""
        events = []
        today = datetime.now().date()
        two_weeks = today + timedelta(days=14)

        for key, meta in self.SERIES.items():
            obs = self.get_series(meta['id'], meta['transform'], limit=3)
            if not obs:
                continue

            latest = obs[0]
            previous = obs[1] if len(obs) > 1 else None

            actual_val = None
            prev_val = None

            try:
                actual_raw = float(latest['value'])
                if meta['unit'] == 'K':
                    actual_val = f"{actual_raw/1000:.0f}K" if meta['transform'] == 'chg' else f"{actual_raw/1000:.1f}K"
                else:
                    actual_val = f"{actual_raw:.1f}%"
            except:
                pass

            try:
                prev_raw = float(previous['value'])
                if meta['unit'] == 'K':
                    prev_val = f"{prev_raw/1000:.0f}K" if meta['transform'] == 'chg' else f"{prev_raw/1000:.1f}K"
                else:
                    prev_val = f"{prev_raw:.1f}%"
            except:
                pass

            release_date_str = latest['date']
            try:
                release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
            except:
                continue

            desc = self.DESCRIPTIONS.get(key, {'en': '', 'ja': ''})

            events.append({
                'date': str(release_date),
                'time': '05:30',
                'name': meta['name'],
                'name_ja': meta['name_ja'],
                'importance': meta['importance'],
                'forecast': None,
                'actual': actual_val,
                'previous': prev_val,
                'unit': meta['unit'],
                'desc_en': desc['en'],
                'desc_ja': desc['ja'],
                'source': 'FRED'
            })

        # Sort by date
        # Sort by date descending (most recent first)
        events.sort(key=lambda x: x['date'], reverse=True)
        return {'updated': str(today), 'events': events}

    def get_macroeconomic_data(self):
        """Legacy method for dashboard compatibility"""
        data = {}
        try:
            import yfinance as yf
            irx = yf.Ticker("^IRX")
            hist = irx.history(period="5d", timeout=10)
            if not hist.empty:
                data['FF_RATE'] = round(hist['Close'].iloc[-1], 2)
            else:
                data['FF_RATE'] = 4.33
        except:
            data['FF_RATE'] = 4.33

        obs_cpi = self.get_series('CPIAUCSL', 'pc1', 2)
        if obs_cpi:
            try: data['CPI'] = round(float(obs_cpi[0]['value']), 2)
            except: data['CPI'] = None

        obs_gdp = self.get_series('A191RL1Q225SBEA', 'lin', 2)
        if obs_gdp:
            try: data['GDP'] = round(float(obs_gdp[0]['value']), 2)
            except: data['GDP'] = None

        obs_unemp = self.get_series('UNRATE', 'lin', 2)
        if obs_unemp:
            try: data['UNEMPLOYMENT'] = round(float(obs_unemp[0]['value']), 2)
            except: data['UNEMPLOYMENT'] = None

        return data