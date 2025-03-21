from app import db
from datetime import datetime
from slugify import slugify

class Page(db.Model):
    """Model for CMS content pages."""
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    meta_description = db.Column(db.String(200))
    featured_image = db.Column(db.String(500))
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    template = db.Column(db.String(50), default='default')  # default, full-width, sidebar
    order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    author = db.relationship('User', foreign_keys=[created_by], backref='pages_created')
    editor = db.relationship('User', foreign_keys=[updated_by], backref='pages_updated')
    
    def __init__(self, *args, **kwargs):
        """Initialize a new page, generating slug if not provided."""
        if 'slug' not in kwargs and 'title' in kwargs:
            kwargs['slug'] = slugify(kwargs['title'])
        super(Page, self).__init__(*args, **kwargs)
    
    def publish(self, user_id):
        """Publish the page."""
        self.status = 'published'
        self.published_at = datetime.utcnow()
        self.updated_by = user_id
    
    def unpublish(self, user_id):
        """Unpublish the page."""
        self.status = 'draft'
        self.updated_by = user_id
    
    def archive(self, user_id):
        """Archive the page."""
        self.status = 'archived'
        self.is_visible = False
        self.updated_by = user_id
    
    def to_dict(self):
        """Convert page to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'meta_description': self.meta_description,
            'featured_image': self.featured_image,
            'status': self.status,
            'template': self.template,
            'order': self.order,
            'is_visible': self.is_visible,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': self.author.username if self.author else None,
            'editor': self.editor.username if self.editor else None
        }
    
    @staticmethod
    def get_templates():
        """Get available page templates."""
        return [
            {'id': 'default', 'name': 'Default Template'},
            {'id': 'full-width', 'name': 'Full Width'},
            {'id': 'sidebar', 'name': 'With Sidebar'},
            {'id': 'landing', 'name': 'Landing Page'}
        ]
    
    @staticmethod
    def get_statuses():
        """Get available page statuses."""
        return [
            {'id': 'draft', 'name': 'Draft'},
            {'id': 'published', 'name': 'Published'},
            {'id': 'archived', 'name': 'Archived'}
        ]
