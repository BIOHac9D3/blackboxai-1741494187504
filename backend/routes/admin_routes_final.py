import os
from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from backend.models.product import Product, Category  # Correcting the import
from backend.models.user import User
from backend.models.page import Page
from backend.forms.cms import CategoryForm, ProductForm, PageForm
from backend import db, cache
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

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_products():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            image=form.image.data.filename,  # Handle file upload separately
            price=form.price.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.manage_products'))
    products = Product.query.all()
    return render_template('admin/products.html', form=form, products=products)
