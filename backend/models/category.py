from sqlalchemy import Column, Integer, String, Text
from backend import db

class Category(db.Model):
    """Category model."""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    def __init__(self, name, slug=None, description=None):
        self.name = name
        self.slug = slug or slugify(name)
        self.description = description

    def __repr__(self):
        return f'<Category {self.name}>'
