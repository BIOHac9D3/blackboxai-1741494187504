from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Order
from app.forms.order import OrderForm

order_bp = Blueprint('order', __name__, url_prefix='/orders')

@order_bp.route('/')
@login_required
def index():
    """List user's orders."""
    if current_user.is_administrator:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id)\
                          .order_by(Order.created_at.desc()).all()
    return render_template('cart/history.html', 
                         title='Order History',
                         orders=orders)

@order_bp.route('/<int:id>')
@login_required
def detail(id):
    """Show order details."""
    order = Order.query.get_or_404(id)
    if not current_user.is_administrator and order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'error')
        return redirect(url_for('order.index'))
    
    return render_template('cart/order_detail.html',
                         title=f'Order #{order.id}',
                         order=order)

@order_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new order."""
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            email=form.email.data,
            shipping_address=form.shipping_address.data,
            billing_address=form.billing_address.data,
            phone=form.phone.data,
            notes=form.notes.data
        )
        db.session.add(order)
        db.session.commit()
        flash('Order created successfully!', 'success')
        return redirect(url_for('order.detail', id=order.id))
    
    return render_template('cart/checkout.html',
                         title='Create Order',
                         form=form)
