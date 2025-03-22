from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category

product_bp = Blueprint('product', __name__, url_prefix='/products')

@product_bp.route('/')
def index():
    """List all active products."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of items per page
    sort = request.args.get('sort', 'newest')
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')

    # Start with base query
    query = Product.query.filter_by(is_active=True)

    # Apply category filter
    if category_id:
        query = query.filter_by(category_id=category_id)

    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )

    # Apply sorting
    if sort == 'price-asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price-desc':
        query = query.order_by(Product.price.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())

    # Get paginated results
    products = query.all()
    categories = Category.query.all()

    return render_template('products/index.html',
                         title='Products',
                         products=products,
                         categories=categories,
                         current_category=category_id)

@product_bp.route('/<slug>')
def detail(slug):
    """Show product details."""
    product = Product.query.filter_by(slug=slug).first_or_404()
    if not product.is_active:
        flash('This product is not available.', 'error')
        return redirect(url_for('product.index'))
    
    related_products = Product.query.filter_by(
        category_id=product.category_id,
        is_active=True
    ).filter(Product.id != product.id).limit(4).all()
    
    return render_template('products/detail.html',
                         title=product.name,
                         product=product,
                         related_products=related_products)

@product_bp.route('/category/<int:id>')
def category(id):
    """List products by category."""
    category = Category.query.get_or_404(id)
    products = Product.query.filter_by(
        category_id=id,
        is_active=True
    ).all()
    categories = Category.query.all()
    
    return render_template('products/index.html',
                         title=f'Category: {category.name}',
                         products=products,
                         categories=categories,
                         current_category=category.id)
