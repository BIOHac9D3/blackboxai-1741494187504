from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models.user import User
from models.product import Product, Category
from models.order import Order, OrderItem
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Get statistics
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_users = User.query.filter_by(role='user').count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Sales statistics for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_sales = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('total')
    ).filter(
        Order.created_at >= thirty_days_ago,
        Order.status == 'paid'
    ).group_by(
        func.date(Order.created_at)
    ).all()
    
    # Format daily sales data for JavaScript
    sales_data = []
    for date, total in daily_sales:
        formatted_date = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        amount = float(total) if total else 0
        sales_data.append([formatted_date, amount])
    
    if request.is_json:
        return jsonify({
            'statistics': {
                'total_orders': total_orders,
                'total_products': total_products,
                'total_users': total_users,
                'daily_sales': sales_data
            }
        })
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         total_products=total_products,
                         total_users=total_users,
                         recent_orders=recent_orders,
                         daily_sales=sales_data)

@admin_bp.route('/products', methods=['GET', 'POST'])
@admin_required
def products():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            stock=int(data['stock']),
            category_id=int(data['category_id']),
            image_url=data.get('image_url'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        if request.is_json:
            return jsonify(product.to_dict()), 201
        flash('Product created successfully')
        return redirect(url_for('admin.products'))
    
    # Get filters
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search', '')
    
    # Build query
    query = Product.query
    
    if category:
        query = query.filter_by(category_id=category)
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    
    if request.is_json:
        return jsonify([product.to_dict() for product in products])
    return render_template('admin/products.html', products=products, categories=categories)

@admin_bp.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'PUT':
        data = request.get_json() if request.is_json else request.form
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.stock = int(data.get('stock', product.stock))
        product.category_id = int(data.get('category_id', product.category_id))
        product.image_url = data.get('image_url', product.image_url)
        product.is_active = data.get('is_active', product.is_active)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify(product.to_dict())
        flash('Product updated successfully')
        return redirect(url_for('admin.products'))
    
    elif request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        
        if request.is_json:
            return '', 204
        flash('Product deleted successfully')
        return redirect(url_for('admin.products'))
    
    if request.is_json:
        return jsonify(product.to_dict())
    return render_template('admin/product_detail.html', product=product)

@admin_bp.route('/orders')
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    
    if request.is_json:
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': orders.page
        })
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/<int:id>', methods=['GET', 'PUT'])
@admin_required
def order(id):
    order = Order.query.get_or_404(id)
    
    if request.method == 'PUT':
        data = request.get_json()
        order.status = data.get('status', order.status)
        db.session.commit()
        
        if request.is_json:
            return jsonify(order.to_dict())
        flash('Order status updated successfully')
        return redirect(url_for('admin.order', id=order.id))
    
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        category = Category(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        
        if request.is_json:
            return jsonify(category.to_dict()), 201
        flash('Category created successfully')
        return redirect(url_for('admin.categories'))
    
    categories = Category.query.all()
    if request.is_json:
        return jsonify([category.to_dict() for category in categories])
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'PUT':
        data = request.get_json() if request.is_json else request.form
        
        category.name = data.get('name', category.name)
        category.slug = data.get('slug', category.slug)
        category.description = data.get('description', category.description)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify(category.to_dict())
        flash('Category updated successfully')
        return redirect(url_for('admin.categories'))
    
    elif request.method == 'DELETE':
        # Check if category has products
        if category.products:
            if request.is_json:
                return jsonify({'error': 'Cannot delete category with products'}), 400
            flash('Cannot delete category with products')
            return redirect(url_for('admin.categories'))
            
        db.session.delete(category)
        db.session.commit()
        
        if request.is_json:
            return '', 204
        flash('Category deleted successfully')
        return redirect(url_for('admin.categories'))
    
    if request.is_json:
        return jsonify(category.to_dict())
    return render_template('admin/category_detail.html', category=category)

@admin_bp.route('/users')
@admin_required
def users():
    users = User.query.filter_by(role='user').all()
    if request.is_json:
        return jsonify([user.to_dict() for user in users])
    return render_template('admin/users.html', users=users)
