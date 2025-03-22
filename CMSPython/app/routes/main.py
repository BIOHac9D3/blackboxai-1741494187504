from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Product, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page."""
    # Get featured products
    featured_products = Product.query.filter_by(
        is_active=True,
        is_featured=True
    ).all()
    
    # Get all categories
    categories = Category.query.all()
    
    return render_template('main/index.html',
                         featured_products=featured_products,
                         categories=categories)

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')

@main_bp.route('/contact', methods=['GET'])
def contact():
    """Contact page."""
    return render_template('main/contact.html')

@main_bp.route('/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submission."""
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # Here you would typically send an email or save to database
    flash('Thank you for your message! We will get back to you soon.', 'success')
    return redirect(url_for('main.contact'))

@main_bp.route('/search')
def search():
    """Search page."""
    query = request.args.get('q', '')
    if not query:
        return render_template('main/search.html', products=[])
    
    products = Product.query.filter(
        Product.is_active == True,
        Product.name.ilike(f'%{query}%')
    ).all()
    
    return render_template('main/search.html',
                         query=query,
                         products=products)
