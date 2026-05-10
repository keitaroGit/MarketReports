import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # API Keys
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    FRED_API_KEY = os.getenv('FRED_API_KEY')
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Cache settings
    CACHE_DIR = 'cache'
    CACHE_TTL = 3600  # 1 hour in seconds
    
    # Update schedule (in minutes)
    UPDATE_INTERVAL = 30  # Update every 30 minutes

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
