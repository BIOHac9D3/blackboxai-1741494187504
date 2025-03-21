import os
from datetime import timedelta

# Additional imports
import logging
from logging.handlers import RotatingFileHandler

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Ensure SECRET_KEY is set for production
    
    # CMS configuration
    CMS_TITLE = os.environ.get('CMS_TITLE', 'ModernStore CMS')
    CMS_ITEMS_PER_PAGE = int(os.environ.get('CMS_ITEMS_PER_PAGE', 10))
    CMS_UPLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/cms/uploads')
    CMS_ALLOWED_FILE_TYPES = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'document': {'pdf', 'doc', 'docx'},
        'media': {'mp4', 'webm', 'mp3'}
    }
    CMS_MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size for CMS uploads
    
    # Rich Text Editor configuration
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 400
    CKEDITOR_FILE_UPLOADER = 'admin.upload'
    
    # Logging configuration
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/cms.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///store.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_TYPE = 'filesystem'
    
    # Security configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'csrf-key-please-change-in-production')
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size for regular uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Stripe configuration
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@modernstore.com')

    @staticmethod
    def init_logging(app):
        """Initialize logging configuration"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        formatter = logging.Formatter(Config.LOG_FORMAT)
        
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.LOG_MAX_SIZE,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CMS startup')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    # Development-specific logging
    @classmethod
    def init_logging(cls, app):
        super().init_logging(app)
        # Add console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)

class ProductionConfig(Config):
    DEBUG = False
    
    # Override these in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    
    # Production logging
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(process)d] %(message)s'
    
    @classmethod
    def init_logging(cls, app):
        super().init_logging(app)
        # Set production log level
        app.logger.setLevel(logging.WARNING)
    
    # Production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:;"
    }

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Returns the appropriate configuration object based on the environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
