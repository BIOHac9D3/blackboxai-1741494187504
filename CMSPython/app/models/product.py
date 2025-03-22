from datetime import datetime
from slugify import slugify
from app import db

class Product(db.Model):
    """Product model."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    category = db.relationship('Category', back_populates='products')
    
    def __init__(self, **kwargs):
        """Initialize product."""
        if 'name' in kwargs:
            # Generate slug from name if not provided
            if 'slug' not in kwargs:
                kwargs['slug'] = slugify(kwargs['name'])
        super(Product, self).__init__(**kwargs)
    
    def __repr__(self):
        """String representation."""
        return f'<Product {self.name}>'
    
    @property
    def formatted_price(self):
        """Return formatted price."""
        return f"${self.price:.2f}"
