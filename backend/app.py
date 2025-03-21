from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from config import get_config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
ckeditor = CKEditor()
csrf = CSRFProtect()
cache = Cache()

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    ckeditor.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

def create_app():
    app = Flask(__name__)
    
    @app.before_request
    def handle_method_override():
        if '_method' in request.form:
            request.environ['REQUEST_METHOD'] = request.form['_method'].upper()
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Register extensions
    register_extensions(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.cms import cms_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(cms_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
