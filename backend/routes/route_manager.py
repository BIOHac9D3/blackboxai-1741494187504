from .admin_routes import admin_bp  # Importing the new admin routes
from .auth import auth_bp
from .cms import cms_bp
from .api import api_bp
from .order import order_bp
from .product_routes import product_bp  # Importing the product routes

blueprints = [
    admin_bp,
    auth_bp,
    cms_bp,
    api_bp,
    order_bp,
    product_bp  # Adding product_bp to the list of blueprints
]

def init_app(app):
    """Initialize the application with all blueprints."""
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
