from datetime import datetime
from app import db

class Category(db.Model):
    """Category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', back_populates='category')
    
    def __repr__(self):
        """String representation."""
        return f'<Category {self.name}>'
