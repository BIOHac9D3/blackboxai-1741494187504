from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from models.product import Product, Category
from models.user import User
from models.page import Page
from forms.cms import CategoryForm, ProductForm, PageForm
from app import db, cache
from sqlalchemy import desc
from datetime import datetime
from slugify import slugify

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator:
            flash('You need administrator privileges to access this area.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
@cache.cached(timeout=300)
def dashboard():
    """Admin dashboard showing key metrics and recent activity"""
    stats = {
        'total_products': Product.query.count(),
        'total_categories': Category.query.count(),
        'total_users': User.query.count(),
        'total_pages': Page.query.count(),
        'recent_products': Product.query.order_by(Product.created_at.desc()).limit(5).all(),
        'recent_users': User.query.order_by(User.created_at.desc()).limit(5).all(),
        'recent_pages': Page.query.order_by(Page.updated_at.desc()).limit(5).all()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """Category management page"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 10)
    
    query = Category.query
    
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Category.name.ilike(f'%{search}%'),
                Category.description.ilike(f'%{search}%')
            )
        )
    
    categories = query.order_by(Category.name).paginate(page=page, per_page=per_page)
    form = CategoryForm()
    
    return render_template('admin/categories.html', categories=categories, form=form)

@admin_bp.route('/categories', methods=['POST'])
@login_required
@admin_required
def create_category():
    """Create a new category"""
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        try:
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error creating category. Please try again.', 'error')
            current_app.logger.error(f'Error creating category: {str(e)}')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:id>')
@login_required
@admin_required
def get_category(id):
    """Get category details for editing"""
    category = Category.query.get_or_404(id)
    return jsonify({
        'name': category.name,
        'slug': category.slug,
        'description': category.description
    })

@admin_bp.route('/categories/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_category(id):
    """Update an existing category"""
    category = Category.query.get_or_404(id)
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            category.name = form.name.data
            category.slug = form.slug.data
            category.description = form.description.data
            category.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Category updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating category. Please try again.', 'error')
            current_app.logger.error(f'Error updating category: {str(e)}')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_category(id):
    """Delete a category"""
    category = Category.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category. Please try again.', 'error')
        current_app.logger.error(f'Error deleting category: {str(e)}')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Product management page"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 10)
    
    query = Product.query
    
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    category_id = request.args.get('category', type=int)
    if category_id:
        query = query.filter(Product.category_id == category_id)

    status = request.args.get('status')
    if status == 'active':
        query = query.filter(Product.is_active == True)
    elif status == 'inactive':
        query = query.filter(Product.is_active == False)
    
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    categories = Category.query.all()
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    return render_template('admin/products.html', products=products.items, categories=categories, form=form)

@admin_bp.route('/products', methods=['POST'])
@login_required
@admin_required
def create_product():
    """Create a new product"""
    data = request.get_json()
    
    try:
        product = Product(
            name=data['name'],
            slug=data['slug'] or slugify(data['name']),
            description=data['description'],
            price=data['price'],
            stock=data['stock'],
            category_id=data['category_id'],
            image=data['image'],
            is_active=data.get('is_active', True),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating product: {str(e)}')
        return jsonify({'error': 'Error creating product'}), 500

@admin_bp.route('/products/<int:id>')
@login_required
@admin_required
def get_product(id):
    """Get product details for editing"""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category_id': product.category_id,
        'image_url': product.image,
        'is_active': product.is_active
    })

@admin_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_product(id):
    """Update an existing product"""
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    try:
        product.name = data['name']
        product.slug = data['slug'] or slugify(data['name'])
        product.description = data['description']
        product.price = data['price']
        product.stock = data['stock']
        product.category_id = data['category_id']
        product.image = data['image']
        product.is_active = data.get('is_active', True)
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating product: {str(e)}')
        return jsonify({'error': 'Error updating product'}), 500

@admin_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(id):
    """Delete a product"""
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting product: {str(e)}')
        return jsonify({'error': 'Error deleting product'}), 500

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 10)
    
    query = User.query
    
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin/users.html', users=users)
