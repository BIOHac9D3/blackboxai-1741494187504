from datetime import datetime
from app import db

class OrderStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    
    CHOICES = [
        PENDING,
        PROCESSING,
        SHIPPED,
        DELIVERED,
        CANCELLED
    ]

class Order(db.Model):
    """Order model."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default=OrderStatus.PENDING)
    total = db.Column(db.Float, default=0.0)
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    customer = db.relationship('User', backref=db.backref('customer_orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    def to_dict(self):
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'status': self.status,
            'total': self.total,
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'phone': self.phone,
            'email': self.email,
            'notes': self.notes,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'customer': self.customer.username if self.customer else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    """Order item model."""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Relationships
    product = db.relationship('Product', backref='order_items')
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
    
    def to_dict(self):
        """Convert order item to dictionary."""
        return {
            'id': self.id,
            'quantity': self.quantity,
            'price': self.price,
            'product': self.product.name if self.product else None,
            'total': self.quantity * self.price
        }
