"""
Macro Data Service - Yahoo Finance fallback
"""
import os
import yfinance as yf
from datetime import datetime, timedelta

class FREDService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('FRED_API_KEY')
    
    def get_macroeconomic_data(self):
        data = {}
        
        # FF金利 - ^IRXは13週物米国債（FF金利の近似値）
        # FF金利
        try:
            irx = yf.Ticker("^IRX")
            hist = irx.history(period="5d", timeout=10)
            if not hist.empty:
                data['FF_RATE'] = round(hist['Close'].iloc[-1], 2)
                data['FF_RATE_date'] = str(hist.index[-1].date())
            else:
                data['FF_RATE'] = 4.33  # フォールバック値
        except Exception as e:
            print(f"Error fetching FF Rate: {e}")
            data['FF_RATE'] = 4.33  # フォールバック値

        # 失業率 - UNRATE ETF代替としてSPYのメタデータから取得困難なため固定値
        # Yahoo Financeでは失業率・CPI・GDPは直接取得不可
        # 最新の公式データを固定値として設定（2025年データ）
        data['CPI'] = 2.4        # YoY %
        data['CPI_MOM'] = 0.1    # MoM % (2025年3月)
        data['CPI_date'] = '2025-03-01'
        data['GDP'] = 2.4        # 2024 Q4 %
        data['GDP_date'] = '2024-12-01'
        data['UNEMPLOYMENT'] = 4.2  # 2025年3月 %
        data['UNEMPLOYMENT_date'] = '2025-03-01'

        return data