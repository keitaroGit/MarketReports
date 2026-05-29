"""
Market Reports Dashboard - Flask Application
Investor-focused dashboard for macro, geopolitical, and sector analysis
"""
from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import os 
import json
import time
from dotenv import load_dotenv
load_dotenv(override=False)
from config import config
from services.fred_service import FREDService
from services.newsapi_service import NewsAPIService
from services.yahoo_service import YahooFinanceService
from services.claude_service import ClaudeService
from services.report_service import ReportService
from utils.cache import CacheManager
from utils.scheduler import UpdateScheduler

# Initialize Flask app
app = Flask(__name__)
CORS(app)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize services
fred_service = FREDService()
newsapi_service = NewsAPIService()
yahoo_service = YahooFinanceService()
report_service = ReportService()
claude_service = ClaudeService()
cache_manager = CacheManager(app.config.get('CACHE_DIR', 'cache'))
scheduler = UpdateScheduler()

# Global data storage
dashboard_data = {
    'macro_overview': None,
    'geopolitical_radar': None,
    'sector_scorecard': None,
    'language': 'en'
}

# ============================================================================
# In-memory cache for company data
# ============================================================================
company_cache = {}
COMPANY_CACHE_TTL = 900  # 15 minutes

def get_company_cached(key):
    if key in company_cache:
        data, timestamp = company_cache[key]
        if time.time() - timestamp < COMPANY_CACHE_TTL:
            return data
    return None

def set_company_cached(key, data):
    company_cache[key] = (data, time.time())

# ============================================================================
# Data Update Functions
# ============================================================================

def update_macro_overview():
    try:
        cache_key = 'macro_overview'
        cached_data = cache_manager.get(cache_key, ttl_seconds=app.config['CACHE_TTL'])
        if cached_data:
            dashboard_data['macro_overview'] = cached_data
            return
        macro_data = fred_service.get_macroeconomic_data()
        commentary = claude_service.generate_macro_commentary(macro_data, language='en')
        commentary_ja = claude_service.generate_macro_commentary(macro_data, language='ja')
        macro_overview = {
            'data': macro_data,
            'commentary': commentary,
            'commentary_ja': commentary_ja
        }
        cache_manager.set(cache_key, macro_overview)
        dashboard_data['macro_overview'] = macro_overview
    except Exception as e:
        print(f"Error updating macro overview: {str(e)}")
        dashboard_data['macro_overview'] = {'error': str(e)}

def update_geopolitical_radar():
    try:
        cache_key = 'geopolitical_radar'
        cached_data = cache_manager.get(cache_key, ttl_seconds=app.config['CACHE_TTL'])
        if cached_data:
            dashboard_data['geopolitical_radar'] = cached_data
            return
        news_items = newsapi_service.get_geopolitical_news(limit=10)
        summary = claude_service.generate_geopolitical_summary(news_items, language='en')
        summary_ja = claude_service.generate_geopolitical_summary(news_items, language='ja')
        geopolitical_radar = {
            'news': news_items,
            'summary': summary,
            'summary_ja': summary_ja
        }
        cache_manager.set(cache_key, geopolitical_radar)
        dashboard_data['geopolitical_radar'] = geopolitical_radar
    except Exception as e:
        print(f"Error updating geopolitical radar: {str(e)}")
        dashboard_data['geopolitical_radar'] = {'error': str(e)}

def update_sector_scorecard():
    try:
        cache_key = 'sector_scorecard'
        cached_data = cache_manager.get(cache_key, ttl_seconds=app.config['CACHE_TTL'])
        if cached_data:
            dashboard_data['sector_scorecard'] = cached_data
            return
        try:
            sector_data = yahoo_service.get_sector_performance()
            if not sector_data:
                sector_data = yahoo_service._get_fallback_data()
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
            sector_data = yahoo_service._get_fallback_data()
        sector_scorecard = {'sectors': sector_data}
        cache_manager.set(cache_key, sector_scorecard)
        dashboard_data['sector_scorecard'] = sector_scorecard
    except Exception as e:
        print(f"Error updating sector scorecard: {str(e)}")
        dashboard_data['sector_scorecard'] = {'error': str(e)}

# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html', language=dashboard_data['language'])

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    language = request.args.get('language', 'en')
    response = {}
    if dashboard_data['macro_overview']:
        macro = dashboard_data['macro_overview'].copy()
        if 'commentary' in macro:
            if language == 'ja':
                macro['commentary'] = macro.get('commentary_ja', macro['commentary'])
            response['macro_overview'] = macro
    if dashboard_data['geopolitical_radar']:
        geo = dashboard_data['geopolitical_radar'].copy()
        if 'summary' in geo:
            if language == 'ja':
                geo['summary'] = geo.get('summary_ja', geo['summary'])
            response['geopolitical_radar'] = geo
    if dashboard_data['sector_scorecard']:
        response['sector_scorecard'] = dashboard_data['sector_scorecard'].copy()
    return jsonify(response)

@app.route('/api/macro-overview', methods=['GET'])
def get_macro_overview():
    language = request.args.get('language', 'en')
    if dashboard_data['macro_overview']:
        data = dashboard_data['macro_overview'].copy()
        if language == 'ja':
            data['commentary'] = data.get('commentary_ja', data.get('commentary', ''))
        return jsonify(data)
    return jsonify({'error': 'No data available'})

@app.route('/api/geopolitical-radar', methods=['GET'])
def get_geopolitical_radar():
    language = request.args.get('language', 'en')
    if dashboard_data['geopolitical_radar']:
        data = dashboard_data['geopolitical_radar'].copy()
        if language == 'ja':
            data['summary'] = data.get('summary_ja', data.get('summary', ''))
        return jsonify(data)
    return jsonify({'error': 'No data available'})

@app.route('/api/sector-scorecard', methods=['GET'])
def get_sector_scorecard():
    language = request.args.get('language', 'en')
    if dashboard_data['sector_scorecard']:
        data = dashboard_data['sector_scorecard'].copy()
        if language == 'ja' and 'sectors' in data:
            for sector in data['sectors']:
                if 'ja_name' in sector:
                    sector['display_name'] = sector['ja_name']
        return jsonify(data)
    return jsonify({'error': 'No data available'})

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    try:
        update_macro_overview()
        update_geopolitical_radar()
        update_sector_scorecard()
        return jsonify({'status': 'success', 'message': 'Data refreshed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    claude_key = os.getenv('CLAUDE_API_KEY', 'NOT_FOUND')
    return jsonify({
        'status': 'healthy',
        'claude_key_exists': bool(claude_key and claude_key != 'NOT_FOUND'),
        'claude_key_prefix': claude_key[:10] if claude_key != 'NOT_FOUND' else 'NOT_FOUND',
        'has_macro': dashboard_data['macro_overview'] is not None,
        'has_geo': dashboard_data['geopolitical_radar'] is not None,
        'has_sectors': dashboard_data['sector_scorecard'] is not None,
    })

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        limit = int(request.args.get('limit', 10))
        news_items = newsapi_service.get_geopolitical_news(limit=limit)
        return jsonify({'status': 'success', 'news': news_items})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/weekly-report', methods=['GET'])
def get_weekly_report():
    language = request.args.get('language', 'en')
    try:
        macro = dashboard_data.get('macro_overview', {})
        geo = dashboard_data.get('geopolitical_radar', {})
        sector = dashboard_data.get('sector_scorecard', {})
        if not macro or not geo or not sector:
            return jsonify({'status': 'error', 'message': 'Data not ready yet'}), 503
        macro_data = macro.get('data', {})
        report = report_service.generate_weekly_report(
            macro_data=macro_data, geo_data=geo, sector_data=sector, language=language
        )
        metadata = report_service.get_report_metadata()
        return Response(
            json.dumps({'status': 'success', 'report': report, 'metadata': metadata}, ensure_ascii=False),
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fedwatch', methods=['GET'])
def get_fedwatch():
    try:
        from services.fedwatch_service import FedWatchService
        fedwatch = FedWatchService()
        current_rate = 4.33
        if dashboard_data['macro_overview']:
            macro = dashboard_data['macro_overview'].get('data', {})
            if macro.get('FF_RATE'):
                current_rate = macro['FF_RATE']
        result = fedwatch.calculate_probabilities(current_rate)
        return jsonify({
            'status': 'success',
            'current_rate': current_rate,
            'ranges': result['ranges'],
            'meetings': result['meetings']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/calendar')
def get_calendar():
    try:
        from services.fred_service import FREDService
        fred = FREDService()
        data = fred.get_calendar_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/company', methods=['GET'])
def get_company():
    ticker = request.args.get('ticker', '').upper().strip()
    if not ticker:
        return jsonify({'status': 'error', 'message': 'Ticker required'}), 400
    try:
        # Check cache first
        cached = get_company_cached(f'fin_{ticker}')
        if cached:
            return jsonify({'status': 'success', 'data': cached, 'cached': True})

        import requests as req
        api_key = os.getenv('ALPHAVANTAGE_API_KEY', 'O4JKJ5C6QPRE5JVG')

        # Company overview
        ov_res = req.get(
            f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}',
            timeout=15
        )
        ov = ov_res.json() if ov_res.status_code == 200 else {}

        time.sleep(0.5)  # 短縮：1秒→0.5秒

        # Global quote (price)
        q_res = req.get(
            f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}',
            timeout=15
        )
        q = q_res.json().get('Global Quote', {}) if q_res.status_code == 200 else {}

        if not ov or not ov.get('Name'):
            return jsonify({'status': 'error', 'message': 'Ticker not found'}), 404

        def fmt(n):
            try:
                n = float(n)
                if abs(n) >= 1e12: return f'${n/1e12:.2f}T'
                if abs(n) >= 1e9: return f'${n/1e9:.2f}B'
                if abs(n) >= 1e6: return f'${n/1e6:.2f}M'
                return f'{n:,.0f}'
            except: return 'N/A'

        try:
            price = float(q.get('05. price', 0)) if q.get('05. price') else None
            prev = float(q.get('08. previous close', 0)) if q.get('08. previous close') else None
        except:
            price = None
            prev = None
        change_pct = ((price - prev) / prev) if price and prev else None

        info = {
            'ticker': ticker,
            'name': ov.get('Name', ticker),
            'sector': ov.get('Sector', 'N/A'),
            'industry': ov.get('Industry', 'N/A'),
            'country': ov.get('Country', 'N/A'),
            'employees': f"{int(ov.get('FullTimeEmployees', 0)):,}" if ov.get('FullTimeEmployees') else 'N/A',
            'price': price,
            'change_pct': change_pct,
            'market_cap': fmt(ov.get('MarketCapitalization')),
            'revenue': fmt(ov.get('RevenueTTM')),
            'net_income': fmt(ov.get('NetIncomeTTM')),
            'pe_ratio': ov.get('TrailingPE', 'N/A'),
            'eps': ov.get('EPS', 'N/A'),
            'dividend_yield': f"{float(ov.get('DividendYield', 0))*100:.2f}%" if ov.get('DividendYield') and ov.get('DividendYield') != 'None' else 'N/A',
            'week52_high': float(ov.get('52WeekHigh', 0)) or None,
            'week52_low': float(ov.get('52WeekLow', 0)) or None,
            'description': ov.get('Description', ''),
            'website': ov.get('OfficialSite', ''),
        }

        # Save to cache
        set_company_cached(f'fin_{ticker}', info)
        return jsonify({'status': 'success', 'data': info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/company-analysis', methods=['GET'])
def get_company_analysis():
    ticker = request.args.get('ticker', '').upper().strip()
    lang = request.args.get('lang', 'en')
    if not ticker:
        return jsonify({'status': 'error', 'message': 'Ticker required'}), 400
    try:
        # Check cache first
        cached = get_company_cached(f'analysis_{ticker}_{lang}')
        if cached:
            return jsonify({'status': 'success', 'data': cached, 'cached': True})

        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))

        if lang == 'ja':
            prompt = f"""{ticker}について以下の情報を調べてJSON形式のみで返してください（前置き・説明・マークダウン不要）：
{{
  "company_name": "正式社名（英語）",
  "industry": "業界（英語）",
  "founded": "設立年",
  "headquarters": "本社所在地（英語）",
  "origin_country": "発祥国（日本語）",
  "overview": "事業概要を日本語3文で記述",
  "products": ["主要製品/サービス1（英語名）", "主要製品/サービス2（英語名）", "主要製品/サービス3（英語名）"],
  "major_customers": ["主要顧客1（英語名）", "主要顧客2（英語名）", "主要顧客3（英語名）"],
  "major_shareholders": ["大株主1（英語名）", "大株主2（英語名）", "大株主3（英語名）"],
  "partners": ["主要パートナー1（英語名）", "主要パートナー2（英語名）", "主要パートナー3（英語名）"],
  "competitors": ["競合1（英語名）", "競合2（英語名）", "競合3（英語名）"],
  "recent_news": ["最近の動向1（日本語で記述）", "最近の動向2（日本語で記述）"]
}}"""
        else:
            prompt = f"""Research {ticker} and respond ONLY with JSON (no preamble, no markdown):
{{
  "company_name": "full company name",
  "industry": "industry sector",
  "founded": "founding year",
  "headquarters": "HQ location",
  "origin_country": "country of origin",
  "overview": "3-sentence business overview",
  "products": ["key product/service 1", "key product/service 2", "key product/service 3"],
  "major_customers": ["major customer 1", "major customer 2", "major customer 3"],
  "major_shareholders": ["major shareholder 1", "major shareholder 2", "major shareholder 3"],
  "partners": ["key partner 1", "key partner 2", "key partner 3"],
  "competitors": ["competitor 1", "competitor 2", "competitor 3"],
  "recent_news": ["recent development 1", "recent development 2"]
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = ''
        for block in message.content:
            if hasattr(block, 'text'):
                result_text += block.text

        clean = result_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean)

        # Save to cache
        set_company_cached(f'analysis_{ticker}_{lang}', data)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/company-widget')
def company_widget():
    return send_from_directory('.', 'company_widget.html')

@app.route('/calendar-widget')
def calendar_widget():
    return send_from_directory('.', 'calendar_widget.html')

@app.route('/fedwatch-widget')
def fedwatch_widget():
    return send_from_directory('.', 'fedwatch_widget.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def initialize_dashboard():
    print("Initializing dashboard data...")
    update_macro_overview()
    update_geopolitical_radar()
    update_sector_scorecard()
    print("Dashboard initialized")

initialize_dashboard()
scheduler.start()
update_interval = app.config.get('UPDATE_INTERVAL', 30)
scheduler.add_job(update_macro_overview, interval_minutes=update_interval, job_id='macro_update')
scheduler.add_job(update_geopolitical_radar, interval_minutes=update_interval, job_id='geo_update')
scheduler.add_job(update_sector_scorecard, interval_minutes=update_interval, job_id='sector_update')

if __name__ == '__main__':
    initialize_dashboard()
    scheduler.start()
    update_interval = app.config.get('UPDATE_INTERVAL', 30)
    scheduler.add_job(update_macro_overview, interval_minutes=update_interval, job_id='macro_update')
    scheduler.add_job(update_geopolitical_radar, interval_minutes=update_interval, job_id='geo_update')
    scheduler.add_job(update_sector_scorecard, interval_minutes=update_interval, job_id='sector_update')
    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    finally:
        scheduler.shutdown()