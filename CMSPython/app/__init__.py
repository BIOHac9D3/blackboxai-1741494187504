import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Handle proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    @login_manager.user_loader
    def load_user(id):
        from app.models import User
        return User.query.get(int(id))
    
    # Register blueprints
    from app.routes import main_bp, auth_bp, admin_bp, cms_bp, api_bp, order_bp, product_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(cms_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(product_bp)
    
    # Context processors
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context."""
        from datetime import datetime
        from app.utils.utils import format_date, format_price
        return dict(
            current_year=datetime.utcnow().year,
            format_date=format_date,
            format_price=format_price
        )
    
    # Request handlers
    @app.before_request
    def before_request():
        """Perform actions before each request."""
        if not request.is_secure and app.env != 'development':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Bad request"), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Unauthorized"), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Forbidden"), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Not found"), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def ratelimit_error(error):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Too many requests"), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Internal server error"), 500
        return render_template('errors/500.html'), 500

    # Set up logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/cms.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CMS startup')
    
    return app

# Import models to ensure they are registered with SQLAlchemy
from app import models
