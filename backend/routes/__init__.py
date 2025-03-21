from .admin import admin_bp
from .auth import auth_bp
from .cms import cms_bp
from .api import api_bp
from .order import order_bp

blueprints = [
    admin_bp,
    auth_bp,
    cms_bp,
    api_bp,
    order_bp
]

def init_app(app):
    """Initialize the application with all blueprints."""
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
