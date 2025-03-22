import os
from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for

from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from backend.models.product import Product
from backend.models.category import Category
from backend.models.user import User
from backend.models.page import Page
from forms.cms import CategoryForm, ProductForm, PageForm
from app import db, cache
from sqlalchemy import desc
from datetime import datetime
from slugify import slugify

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

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
    """Create a new product with image upload support"""
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            # Handle image upload
            image_path = None
            if form.image.data:
                if allowed_file(form.image.data.filename):
                    image_path = save_file(
                        form.image.data,
                        folder='products',
                        is_image=True,
                        max_size=(800, 800)
                    )
                    if image_path:
                        # Create thumbnail
                        original_path = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            'products',
                            os.path.basename(image_path)
                        )
                        create_thumbnail(original_path, size=(200, 200))
            elif form.image_url.data:
                image_path = form.image_url.data

            # Create product
            product = Product(
                name=form.name.data,
                slug=form.slug.data or slugify(form.name.data),
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data,
                category_id=form.category_id.data,
                image=image_path,
                is_active=form.is_active.data
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('Product created successfully.', 'success')
            return jsonify({
                'status': 'success',
                'message': 'Product created successfully',
                'product': product.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating product: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while creating the product. Please try again.',
                'error': str(e)
            }), 500
    
    # If form validation failed, return errors
    errors = {field.name: field.errors for field in form if field.errors}
    return jsonify({
        'status': 'error',
        'message': 'Validation failed',
        'errors': errors
    }), 400

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
    """Update an existing product with image upload support"""
    product = Product.query.get_or_404(id)
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            # Handle image upload
            if form.image.data:
                if allowed_file(form.image.data.filename):
                    # Delete old image and its thumbnail if exists
                    if product.image and product.image.startswith('/static/uploads/'):
                        old_file_path = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            'products',
                            os.path.basename(product.image)
                        )
                        old_thumb_path = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            'products/thumbnails',
                            f"thumb_{os.path.basename(product.image)}"
                        )
                        delete_file(old_file_path)
                        delete_file(old_thumb_path)
                    
                    # Save new image
                    image_path = save_file(
                        form.image.data,
                        folder='products',
                        is_image=True,
                        max_size=(800, 800)
                    )
                    if image_path:
                        product.image = image_path
                        # Create thumbnail
                        original_path = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            'products',
                            os.path.basename(image_path)
                        )
                        create_thumbnail(original_path, size=(200, 200))
            elif form.image_url.data:
                product.image = form.image_url.data

            # Update product
            product.name = form.name.data
            product.slug = form.slug.data or slugify(form.name.data)
            product.description = form.description.data
            product.price = form.price.data
            product.stock = form.stock.data
            product.category_id = form.category_id.data
            product.is_active = form.is_active.data
            product.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Product updated successfully.', 'success')
            return jsonify({
                'status': 'success',
                'message': 'Product updated successfully',
                'product': product.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating product: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while updating the product. Please try again.',
                'error': str(e)
            }), 500
    
    # If form validation failed, return errors
    errors = {field.name: field.errors for field in form if field.errors}
    return jsonify({
        'status': 'error',
        'message': 'Validation failed',
        'errors': errors
    }), 400

@admin_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(id):
    """Delete a product and its associated files"""
    product = Product.query.get_or_404(id)
    try:
        # Delete associated image and thumbnail if they exist
        if product.image and product.image.startswith('/static/uploads/'):
            # Delete main image
            image_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'products',
                os.path.basename(product.image)
            )
            delete_file(image_path)
            
            # Delete thumbnail
            thumb_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                'products/thumbnails',
                f"thumb_{os.path.basename(product.image)}"
            )
            delete_file(thumb_path)

        # Delete product from database
        db.session.delete(product)
        db.session.commit()
        
        flash('Product deleted successfully.', 'success')
        return jsonify({
            'status': 'success',
            'message': 'Product deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting product: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while deleting the product.',
            'error': str(e)
        }), 500

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
