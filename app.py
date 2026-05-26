"""
Market Reports Dashboard - Flask Application
Investor-focused dashboard for macro, geopolitical, and sector analysis
"""
from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import os 
import json
from dotenv import load_dotenv
load_dotenv(override=False)  # 既存の環境変数を上書きしない
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
# Data Update Functions
# ============================================================================

def update_macro_overview():
    """Fetch and update macro overview data"""
    try:
        # Try to get from cache first
        cache_key = 'macro_overview'
        cached_data = cache_manager.get(cache_key, ttl_seconds=app.config['CACHE_TTL'])
        
        if cached_data:
            dashboard_data['macro_overview'] = cached_data
            return
        
        # Fetch fresh data from FRED
        macro_data = fred_service.get_macroeconomic_data()
        
        # Generate AI commentary
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
    """Fetch and update geopolitical news"""
    try:
        # Try to get from cache first
        cache_key = 'geopolitical_radar'
        cached_data = cache_manager.get(cache_key, ttl_seconds=app.config['CACHE_TTL'])
        
        if cached_data:
            dashboard_data['geopolitical_radar'] = cached_data
            return
        
        # Fetch news
        news_items = newsapi_service.get_geopolitical_news(limit=10)
        
        # Generate AI summary
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
    """Fetch and update sector performance data"""
    try:
        # Try to get from cache first
        cache_key = 'sector_scorecard'
        cached_data = cache_manager.get(cache_key, ttl_seconds=app.config['CACHE_TTL'])
        
        if cached_data:
            dashboard_data['sector_scorecard'] = cached_data
            return
        
        # Fetch sector data
        try:
            sector_data = yahoo_service.get_sector_performance()
            if not sector_data:
                sector_data = yahoo_service._get_fallback_data()
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
            sector_data = yahoo_service._get_fallback_data()
        
        sector_scorecard = {
            'sectors': sector_data
        }
        
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
    """Render main dashboard"""
    return render_template('index.html', language=dashboard_data['language'])

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get all dashboard data"""
    language = request.args.get('language', 'en')
    
    response = {}
    
    # Macro Overview
    if dashboard_data['macro_overview']:
        macro = dashboard_data['macro_overview'].copy()
        if 'commentary' in macro:
            if language == 'ja':
                macro['commentary'] = macro.get('commentary_ja', macro['commentary'])
            response['macro_overview'] = macro
    
    # Geopolitical Radar
    if dashboard_data['geopolitical_radar']:
        geo = dashboard_data['geopolitical_radar'].copy()
        if 'summary' in geo:
            if language == 'ja':
                geo['summary'] = geo.get('summary_ja', geo['summary'])
            response['geopolitical_radar'] = geo
    
    # Sector Scorecard
    if dashboard_data['sector_scorecard']:
        response['sector_scorecard'] = dashboard_data['sector_scorecard'].copy()
    
    return jsonify(response)

@app.route('/api/macro-overview', methods=['GET'])
def get_macro_overview():
    """Get macro overview data"""
    language = request.args.get('language', 'en')
    
    if dashboard_data['macro_overview']:
        data = dashboard_data['macro_overview'].copy()
        if language == 'ja':
            data['commentary'] = data.get('commentary_ja', data.get('commentary', ''))
        return jsonify(data)
    
    return jsonify({'error': 'No data available'})

@app.route('/api/geopolitical-radar', methods=['GET'])
def get_geopolitical_radar():
    """Get geopolitical radar data"""
    language = request.args.get('language', 'en')
    
    if dashboard_data['geopolitical_radar']:
        data = dashboard_data['geopolitical_radar'].copy()
        if language == 'ja':
            data['summary'] = data.get('summary_ja', data.get('summary', ''))
        return jsonify(data)
    
    return jsonify({'error': 'No data available'})

@app.route('/api/sector-scorecard', methods=['GET'])
def get_sector_scorecard():
    """Get sector scorecard data"""
    language = request.args.get('language', 'en')
    
    if dashboard_data['sector_scorecard']:
        data = dashboard_data['sector_scorecard'].copy()
        
        # Add localized sector names if requested
        if language == 'ja' and 'sectors' in data:
            for sector in data['sectors']:
                if 'ja_name' in sector:
                    sector['display_name'] = sector['ja_name']
        
        return jsonify(data)
    
    return jsonify({'error': 'No data available'})

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Manually refresh all data"""
    try:
        update_macro_overview()
        update_geopolitical_radar()
        update_sector_scorecard()
        return jsonify({'status': 'success', 'message': 'Data refreshed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    import os
    claude_key = os.getenv('CLAUDE_API_KEY', 'NOT_FOUND')
    return jsonify({
        'status': 'healthy',
        'claude_key_exists': bool(claude_key and claude_key != 'NOT_FOUND'),
        'claude_key_prefix': claude_key[:10] if claude_key != 'NOT_FOUND' else 'NOT_FOUND',
        'has_macro': dashboard_data['macro_overview'] is not None,
        'has_geo': dashboard_data['geopolitical_radar'] is not None,
        'has_sectors': dashboard_data['sector_scorecard'] is not None,
    })
# ============================================================================
# Initialization and Error Handling
# ============================================================================
@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest news for external use (Wix etc.)"""
    try:
        limit = int(request.args.get('limit', 10))
        news_items = newsapi_service.get_geopolitical_news(limit=limit)
        return jsonify({
            'status': 'success',
            'news': news_items
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/api/weekly-report', methods=['GET'])
def get_weekly_report():
    """Generate weekly market report"""
    language = request.args.get('language', 'en')
    
    try:
        macro = dashboard_data.get('macro_overview', {})
        geo = dashboard_data.get('geopolitical_radar', {})
        sector = dashboard_data.get('sector_scorecard', {})
        
        if not macro or not geo or not sector:
            return jsonify({'status': 'error', 'message': 'Data not ready yet'}), 503
        
        macro_data = macro.get('data', {})
        report = report_service.generate_weekly_report(
            macro_data=macro_data,
            geo_data=geo,
            sector_data=sector,
            language=language
        )
        metadata = report_service.get_report_metadata()
        
        return Response(
            json.dumps({
                'status': 'success',
                'report': report,
                'metadata': metadata
            }, ensure_ascii=False),
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500   
    
@app.route('/api/fedwatch', methods=['GET'])
def get_fedwatch():
    """Get Fed rate probability data from FF futures"""
    try:
        from services.fedwatch_service import FedWatchService
        fedwatch = FedWatchService()
        current_rate = 4.33  # Current FF rate
        
        # Check macro data for current rate
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
        import requests as req
        api_key = os.getenv('FINNHUB_API_KEY')
        headers = {'X-Finnhub-Token': api_key}

        # Quote (price)
        quote_res = req.get(f'https://finnhub.io/api/v1/quote?symbol={ticker}', headers=headers, timeout=10)
        quote = quote_res.json() if quote_res.status_code == 200 else {}

        # Company profile
        profile_res = req.get(f'https://finnhub.io/api/v1/stock/profile2?symbol={ticker}', headers=headers, timeout=10)
        profile = profile_res.json() if profile_res.status_code == 200 else {}

        # Basic financials
        fin_res = req.get(f'https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all', headers=headers, timeout=10)
        fin = fin_res.json().get('metric', {}) if fin_res.status_code == 200 else {}

        if not profile or not profile.get('name'):
            return jsonify({'status': 'error', 'message': 'Ticker not found'}), 404

        def fmt(n):
            if n is None: return 'N/A'
            if abs(n) >= 1e12: return f'${n/1e12:.2f}T'
            if abs(n) >= 1e9: return f'${n/1e9:.2f}B'
            if abs(n) >= 1e6: return f'${n/1e6:.2f}M'
            return f'{n:,.0f}'

        price = quote.get('c')
        prev = quote.get('pc')
        change_pct = ((price - prev) / prev) if price and prev else None

        mktcap = profile.get('marketCapitalization')
        mktcap_fmt = fmt(mktcap * 1e6) if mktcap else 'N/A'

        info = {
            'ticker': ticker,
            'name': profile.get('name', ticker),
            'sector': profile.get('finnhubIndustry', 'N/A'),
            'industry': profile.get('finnhubIndustry', 'N/A'),
            'country': profile.get('country', 'N/A'),
            'employees': f"{profile.get('employeeTotal', 0):,}" if profile.get('employeeTotal') else 'N/A',
            'price': price,
            'change_pct': change_pct,
            'market_cap': mktcap_fmt,
            'revenue': fmt(fin.get('revenuePerShareTTM') and fin.get('revenuePerShareTTM') * fin.get('shareOutstanding', 0) * 1e6),
            'net_income': 'N/A',
            'pe_ratio': round(fin.get('peTTM'), 1) if fin.get('peTTM') else 'N/A',
            'eps': round(fin.get('epsTTM'), 2) if fin.get('epsTTM') else 'N/A',
            'dividend_yield': f"{fin.get('dividendYieldIndicatedAnnual', 0):.2f}%" if fin.get('dividendYieldIndicatedAnnual') else 'N/A',
            'week52_high': fin.get('52WeekHigh'),
            'week52_low': fin.get('52WeekLow'),
            'description': f"{profile.get('name')} is listed on {profile.get('exchange')} under ticker {ticker}. Industry: {profile.get('finnhubIndustry')}. IPO: {profile.get('ipo')}. Website: {profile.get('weburl')}",
            'website': profile.get('weburl', ''),
        }
        return jsonify({'status': 'success', 'data': info})
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
    """Initialize all dashboard data on startup"""
    print("Initializing dashboard data...")
    update_macro_overview()
    update_geopolitical_radar()
    update_sector_scorecard()
    print("Dashboard initialized")
# Initialize for gunicorn
initialize_dashboard()
scheduler.start()
update_interval = app.config.get('UPDATE_INTERVAL', 30)
scheduler.add_job(update_macro_overview, interval_minutes=update_interval, job_id='macro_update')
scheduler.add_job(update_geopolitical_radar, interval_minutes=update_interval, job_id='geo_update')
scheduler.add_job(update_sector_scorecard, interval_minutes=update_interval, job_id='sector_update')

if __name__ == '__main__':

    # Initialize data
    initialize_dashboard()
    
    # Start scheduler
    scheduler.start()
    
    # Schedule periodic updates (every 30 minutes by default)
    update_interval = app.config.get('UPDATE_INTERVAL', 30)
    scheduler.add_job(update_macro_overview, interval_minutes=update_interval, job_id='macro_update')
    scheduler.add_job(update_geopolitical_radar, interval_minutes=update_interval, job_id='geo_update')
    scheduler.add_job(update_sector_scorecard, interval_minutes=update_interval, job_id='sector_update')
    
    # Run Flask app
    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    finally:
        scheduler.shutdown()
