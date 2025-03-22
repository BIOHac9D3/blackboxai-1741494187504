import os
from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from PIL import Image

def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator:
            flash('You need administrator privileges to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, filename):
    """Save uploaded image to filesystem."""
    try:
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'])
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        return filepath
    except Exception as e:
        current_app.logger.error(f'Error saving image: {str(e)}')
        return None

def create_thumbnail(filepath, size=(200, 200)):
    """Create thumbnail for uploaded image."""
    try:
        thumb_path = os.path.join(os.path.dirname(filepath), 'thumbnails')
        if not os.path.exists(thumb_path):
            os.makedirs(thumb_path)
            
        filename = os.path.basename(filepath)
        thumb_filepath = os.path.join(thumb_path, f'thumb_{filename}')
        
        with Image.open(filepath) as img:
            img.thumbnail(size)
            img.save(thumb_filepath)
            
        return thumb_filepath
    except Exception as e:
        current_app.logger.error(f'Error creating thumbnail: {str(e)}')
        return None
