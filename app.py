"""
Market Reports Dashboard - Flask Application
Investor-focused dashboard for macro, geopolitical, and sector analysis
"""
from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv
load_dotenv()
from config import config
from services.fred_service import FREDService
from services.newsapi_service import NewsAPIService
from services.yahoo_service import YahooFinanceService
from services.claude_service import ClaudeService
from utils.cache import CacheManager
from utils.scheduler import UpdateScheduler

# Initialize Flask app
app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize services
fred_service = FREDService()
newsapi_service = NewsAPIService()
yahoo_service = YahooFinanceService()
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
        sector_data = yahoo_service.get_sector_performance()
        
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
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'has_macro': dashboard_data['macro_overview'] is not None,
        'has_geo': dashboard_data['geopolitical_radar'] is not None,
        'has_sectors': dashboard_data['sector_scorecard'] is not None
    })

# ============================================================================
# Initialization and Error Handling
# ============================================================================

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
