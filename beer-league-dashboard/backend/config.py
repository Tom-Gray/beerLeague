import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Flask application."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bench_scoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Data directory settings
    DATA_DIR = os.environ.get('DATA_DIR') or str(Path(__file__).parent.parent.parent / 'stats-sleeper' / 'data')
    
    @classmethod
    def get_absolute_data_dir(cls):
        """Get absolute path to data directory."""
        return str(Path(__file__).parent.parent.parent / 'stats-sleeper' / 'data')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # API settings
    API_TITLE = 'Beer League Bench Scoring API'
    API_VERSION = 'v1'
    API_DESCRIPTION = 'REST API for fantasy football bench scoring data'
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def validate_config():
        """Validate configuration settings."""
        config = Config()
        
        # Check if data directory exists
        data_dir = Path(config.DATA_DIR)
        if not data_dir.exists():
            raise ValueError(f"Data directory does not exist: {config.DATA_DIR}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
