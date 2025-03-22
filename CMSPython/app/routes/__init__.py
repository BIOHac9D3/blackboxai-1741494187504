"""Route blueprints for the application."""
from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .cms import cms_bp
from .api import api_bp
from .order import order_bp
from .product import product_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'admin_bp',
    'cms_bp',
    'api_bp',
    'order_bp',
    'product_bp'
]
