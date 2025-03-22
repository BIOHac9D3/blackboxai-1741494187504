from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Order, Page
from app.forms.cms import CategoryForm, ProductForm, PageForm, MediaUploadForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    """Ensure user is an administrator."""
    if not current_user.is_administrator:
        flash('You must be an administrator to access this area.', 'error')
        return redirect(url_for('main.index'))

@admin_bp.route('/')
def dashboard():
    """Admin dashboard."""
    products_count = Product.query.count()
    orders_count = Order.query.count()
    pages_count = Page.query.count()
    categories_count = Category.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         title='Dashboard',
                         products_count=products_count,
                         orders_count=orders_count,
                         pages_count=pages_count,
                         categories_count=categories_count,
                         recent_orders=recent_orders)

@admin_bp.route('/products')
def manage_products():
    """Manage products."""
    products = Product.query.order_by(Product.name).all()
    return render_template('admin/products.html',
                         title='Manage Products',
                         products=products)

@admin_bp.route('/categories')
def manage_categories():
    """Manage categories."""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html',
                         title='Manage Categories',
                         categories=categories)

@admin_bp.route('/orders')
def manage_orders():
    """Manage orders."""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html',
                         title='Manage Orders',
                         orders=orders)

@admin_bp.route('/pages')
def manage_pages():
    """Manage CMS pages."""
    pages = Page.query.order_by(Page.title).all()
    return render_template('admin/pages.html',
                         title='Manage Pages',
                         pages=pages)

@admin_bp.route('/media')
def manage_media():
    """Manage media files."""
    form = MediaUploadForm()
    return render_template('admin/media.html',
                         title='Media Library',
                         form=form)
