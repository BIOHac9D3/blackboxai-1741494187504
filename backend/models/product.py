from sqlalchemy import Column, Integer, String, Text, Float
from backend import db
from datetime import datetime
from slugify import slugify

class Product(db.Model):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    image = Column(String(500))
    is_active = Column(db.Boolean, default=True)
    is_featured = Column(db.Boolean, default=False)  # New property for featured products
    category_id = Column(Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, slug=None, description=None, price=0.0, stock=0, image=None, category_id=None, is_active=True):
        self.name = name
        self.slug = slug or slugify(name)
        self.description = description
        self.price = price
        self.stock = stock
        self.image = image
        self.category_id = category_id
        self.is_active = is_active

    def __repr__(self):
        return f'<Product {self.name}>'

    # Relationships
    category = db.relationship('Category', backref='products', lazy=True)

    def to_dict(self):
        """Convert product to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'image': self.image,
            'is_active': self.is_active,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create a new product from dictionary data"""
        return Product(
            name=data.get('name'),
            slug=data.get('slug'),
            description=data.get('description'),
            price=data.get('price', 0.0),
            stock=data.get('stock', 0),
            image=data.get('image'),
            category_id=data.get('category_id'),
            is_active=data.get('is_active', True)
        )
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, slug=None, description=None, price=0.0, stock=0, image=None, category_id=None, is_active=True):
        self.name = name
        self.slug = slug or slugify(name)
        self.description = description
        self.price = price
        self.stock = stock
        self.image = image
        self.category_id = category_id
        self.is_active = is_active

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        """Convert product to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'image': self.image,
            'is_active': self.is_active,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create a new product from dictionary data"""
        return Product(
            name=data.get('name'),
            slug=data.get('slug'),
            description=data.get('description'),
            price=data.get('price', 0.0),
            stock=data.get('stock', 0),
            image=data.get('image'),
            category_id=data.get('category_id'),
            is_active=data.get('is_active', True)
        )
