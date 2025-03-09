from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from models.product import Product, Category
from models.order import Order, OrderItem, CartItem
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Product endpoints
@api_bp.route('/products')
def get_products():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    if sort == 'price':
        query = query.order_by(Product.price.desc() if order == 'desc' else Product.price.asc())
    else:
        query = query.order_by(Product.created_at.desc() if order == 'desc' else Product.created_at.asc())
    
    products = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'products': [product.to_dict() for product in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })

@api_bp.route('/products/<int:id>')
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())

# Category endpoints
@api_bp.route('/categories')
def get_categories():
    categories = Category.query.filter_by(parent_id=None).all()
    return jsonify([category.to_dict() for category in categories])

# Cart endpoints
@api_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'POST':
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        product = Product.query.get_or_404(product_id)
        if product.stock < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if cart_item:
            cart_item.quantity = quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify(cart_item.to_dict())
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([item.to_dict() for item in cart_items])

@api_bp.route('/cart/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def cart_item(id):
    cart_item = CartItem.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    if request.method == 'PUT':
        data = request.get_json()
        quantity = data.get('quantity', 1)
        
        if cart_item.product.stock < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        return jsonify(cart_item.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(cart_item)
        db.session.commit()
        return '', 204

# Order endpoints
@api_bp.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == 'POST':
        data = request.get_json()
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Calculate total amount
        total_amount = sum(item.subtotal for item in cart_items)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_address=data['shipping_address'],
            billing_address=data.get('billing_address') or data['shipping_address']
        )
        db.session.add(order)
        
        # Create order items
        for cart_item in cart_items:
            if cart_item.product.stock < cart_item.quantity:
                db.session.rollback()
                return jsonify({
                    'error': f'Not enough stock for {cart_item.product.name}'
                }), 400
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
            
            # Remove cart item
            db.session.delete(cart_item)
        
        db.session.commit()
        return jsonify(order.to_dict()), 201
    
    # GET request - return user's orders
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return jsonify({
        'orders': [order.to_dict() for order in orders.items],
        'total': orders.total,
        'pages': orders.pages,
        'current_page': orders.page
    })

@api_bp.route('/orders/<int:id>')
@login_required
def get_order(id):
    order = Order.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    return jsonify(order.to_dict())

# Search endpoints
@api_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%') |
        Product.description.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'category': p.category.name
    } for p in products])

# User profile endpoints
@api_bp.route('/profile')
@login_required
def get_profile():
    return jsonify(current_user.to_dict())

@api_bp.route('/profile/orders')
@login_required
def get_profile_orders():
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc())\
        .limit(5).all()
    return jsonify([order.to_dict() for order in orders])
