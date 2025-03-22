import os
from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from backend.models.product import Product
from backend.forms.cms import ProductForm
from backend import db

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('product.manage_products'))
    products = Product.query.all()
    return render_template('admin/products.html', form=form, products=products, title='Manage Products')
