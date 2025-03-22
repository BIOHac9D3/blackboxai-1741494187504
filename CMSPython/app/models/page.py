from datetime import datetime
from slugify import slugify
from app import db

class Page(db.Model):
    """Page model."""
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    meta_description = db.Column(db.String(160))
    template = db.Column(db.String(50), default='default.html')
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, **kwargs):
        """Initialize a new page."""
        super(Page, self).__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = slugify(self.title)
    
    def __repr__(self):
        return f'<Page {self.title}>'
    
    def to_dict(self):
        """Convert page to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'meta_description': self.meta_description,
            'template': self.template,
            'published': self.published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def get_templates():
        """Get list of available templates."""
        return [
            {'file': 'default.html', 'name': 'Default Template'},
            {'file': 'full-width.html', 'name': 'Full Width'},
            {'file': 'sidebar.html', 'name': 'With Sidebar'},
            {'file': 'landing.html', 'name': 'Landing Page'},
            {'file': 'blog.html', 'name': 'Blog Post'}
        ]
