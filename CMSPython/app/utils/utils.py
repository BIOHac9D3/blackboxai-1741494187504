import os
from functools import wraps
from PIL import Image
from flask import current_app, flash, redirect, url_for
from flask_login import current_user

def format_price(price):
    """Format price with 2 decimal places and currency symbol."""
    return f"${price:.2f}"

def format_date(date):
    """Format date in a readable format."""
    return date.strftime("%B %d, %Y")

def admin_required(f):
    """Decorator to require admin access for views."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator:
            flash('You need administrator privileges to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder):
    """Save uploaded image to specified folder."""
    if not file:
        return None
    
    filename = file.filename
    if filename and allowed_file(filename):
        # Create unique filename
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{os.urandom(16).hex()}.{ext}"
        
        # Ensure upload folder exists
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)
        
        return f"{folder}/{new_filename}"
    return None

def create_thumbnail(image_path, size=(200, 200)):
    """Create a thumbnail of the specified size."""
    if not image_path:
        return None
        
    try:
        # Get full path
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
        
        # Open image
        img = Image.open(full_path)
        
        # Create thumbnail
        img.thumbnail(size)
        
        # Save thumbnail
        thumb_path = f"{os.path.splitext(full_path)[0]}_thumb{os.path.splitext(full_path)[1]}"
        img.save(thumb_path)
        
        # Return relative path
        return f"{os.path.splitext(image_path)[0]}_thumb{os.path.splitext(image_path)[1]}"
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail: {str(e)}")
        return None
