from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from werkzeug.exceptions import NotFound
from models.order import Order, OrderItem
from models.product import Product
from models.user import User
from forms.order import OrderForm
from utils import admin_required
from app import db

order_bp = Blueprint('order', __name__, url_prefix='/admin/orders')

@order_bp.route('/')
@login_required
@admin_required
def orders():
    """List all orders with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build query with filters
    query = Order.query
    
    status = request.args.get('status')
    if status:
        query = query.filter(Order.status == status)
    
    payment_status = request.args.get('payment_status')
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    
    date = request.args.get('date')
    if date:
        query = query.filter(db.func.date(Order.created_at) == date)
    
    search = request.args.get('search')
    if search:
        query = query.join(Order.user).filter(
            db.or_(
                Order.id.like(f'%{search}%'),
                User.name.like(f'%{search}%'),
                User.email.like(f'%{search}%')
            )
        )
    
    # Order by most recent first
    query = query.order_by(Order.created_at.desc())
    
    # Paginate results
    orders = query.paginate(page=page, per_page=per_page)
    
    # Get all products and users for the order form
    products = Product.query.filter_by(is_active=True).all()
    users = User.query.filter_by(is_active=True).all()
    
    return render_template('admin/orders.html', 
                         orders=orders,
                         products=products,
                         users=users)

@order_bp.route('/<int:id>')
@login_required
@admin_required
def get_order(id):
    """Get order details"""
    order = Order.query.get_or_404(id)
    
    return jsonify(order.to_dict())

@order_bp.route('/', methods=['POST'])
@login_required
@admin_required
def create_order():
    """Create a new order"""
    form = OrderForm()
    
    if form.validate_on_submit():
        try:
            order = Order(
                user_id=form.user_id.data,
                status=form.status.data,
                payment_status=form.payment_status.data,
                shipping_address=form.shipping_address.data,
                billing_address=form.billing_address.data,
                total_amount=form.total_amount.data
            )
            
            # Process order items
            items_data = []
            i = 0
            while f'items[{i}][product_id]' in request.form:
                items_data.append({
                    'product_id': request.form[f'items[{i}][product_id]'],
                    'quantity': request.form[f'items[{i}][quantity]'],
                    'price': request.form[f'items[{i}][price]']
                })
                i += 1

            for item_data in items_data:
                item = OrderItem(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                order.items.append(item)
            
            db.session.add(order)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Order created successfully',
                'order': order.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating order: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while creating the order'
            }), 500
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid form data',
        'errors': form.errors
    }), 400

@order_bp.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_order(id):
    """Update an existing order"""
    order = Order.query.get_or_404(id)
    form = OrderForm()
    
    if form.validate_on_submit():
        try:
            order.status = form.status.data
            order.payment_status = form.payment_status.data
            order.shipping_address = form.shipping_address.data
            order.billing_address = form.billing_address.data
            order.total_amount = form.total_amount.data
            
            # Update order items
            # First, remove all existing items
            OrderItem.query.filter_by(order_id=order.id).delete()
            
            # Process order items
            items_data = []
            i = 0
            while f'items[{i}][product_id]' in request.form:
                items_data.append({
                    'product_id': request.form[f'items[{i}][product_id]'],
                    'quantity': request.form[f'items[{i}][quantity]'],
                    'price': request.form[f'items[{i}][price]']
                })
                i += 1

            for item_data in items_data:
                item = OrderItem(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                order.items.append(item)
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Order updated successfully',
                'order': order.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating order: {str(e)}')
            return jsonify({
                'status': 'error',
                'message': 'An error occurred while updating the order'
            }), 500
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid form data',
        'errors': form.errors
    }), 400

@order_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_order(id):
    """Delete an order"""
    order = Order.query.get_or_404(id)
    
    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Order deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting order: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while deleting the order'
        }), 500

@order_bp.route('/export')
@login_required
@admin_required
def export_orders():
    """Export orders as CSV"""
    import csv
    from io import StringIO
    from datetime import datetime
    
    # Apply filters
    query = Order.query
    
    status = request.args.get('status')
    if status:
        query = query.filter(Order.status == status)
    
    payment_status = request.args.get('payment_status')
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    
    date = request.args.get('date')
    if date:
        query = query.filter(db.func.date(Order.created_at) == date)
    
    search = request.args.get('search')
    if search:
        query = query.join(Order.user).filter(
            db.or_(
                Order.id.like(f'%{search}%'),
                User.name.like(f'%{search}%'),
                User.email.like(f'%{search}%')
            )
        )
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Order ID',
        'Date',
        'Customer',
        'Status',
        'Payment Status',
        'Total Amount',
        'Items'
    ])
    
    # Write data
    for order in query.all():
        writer.writerow([
            order.id,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            f"{order.user.name} ({order.user.email})",
            order.status,
            order.payment_status,
            f"${order.total_amount:.2f}",
            ', '.join(f"{item.quantity}x {item.product.name}" for item in order.items)
        ])
    
    # Create response
    from flask import make_response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response
