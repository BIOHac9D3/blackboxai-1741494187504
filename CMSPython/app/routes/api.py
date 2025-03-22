from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Order, Page

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/products')
def get_products():
    """Get list of products."""
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/categories')
def get_categories():
    """Get list of categories."""
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])

@api_bp.route('/pages')
def get_pages():
    """Get list of published pages."""
    pages = Page.query.filter_by(published=True).all()
    return jsonify([page.to_dict() for page in pages])

@api_bp.route('/orders')
@login_required
def get_orders():
    """Get list of user's orders."""
    if current_user.is_administrator:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).all()
    return jsonify([order.to_dict() for order in orders])
