import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app
import jwt
from datetime import datetime, timedelta
import re
from functools import wraps
from flask import jsonify, request
from flask_login import current_user

def generate_unique_filename(filename):
    """Generate a unique filename while preserving the original extension."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return f"{uuid.uuid4().hex}.{ext}"

def allowed_file(filename, allowed_types=None):
    """
    Check if the file extension is allowed.
    
    Args:
        filename: The name of the file to check
        allowed_types: Optional dict of allowed file types by category (e.g., {'image': ['.jpg', '.png']})
                      If None, uses ALLOWED_EXTENSIONS from config
    """
    if not '.' in filename:
        return False
        
    ext = filename.rsplit('.', 1)[1].lower()
    
    if allowed_types:
        # Check against all categories in allowed_types
        return any(ext in types for types in allowed_types.values())
    
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder='uploads', is_image=True, max_size=None):
    """
    Save a file and return its path.
    
    Args:
        file: The file object to save
        folder: The subfolder to save the file in
        is_image: Whether the file is an image (will be processed if True)
        max_size: Optional tuple of (width, height) for max image dimensions
    """
    if not file:
        return None
        
    filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(filename)
    
    # Create folder if it doesn't exist
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(folder_path, exist_ok=True)
    
    filepath = os.path.join(folder_path, unique_filename)
    
    try:
        if is_image:
            image = Image.open(file)
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            # Resize if dimensions are provided
            if max_size:
                image.thumbnail(max_size)
            
            # Save with optimization
            image.save(filepath, optimize=True, quality=85)
        else:
            file.save(filepath)
            
        return f"/static/uploads/{folder}/{unique_filename}"
    except Exception as e:
        current_app.logger.error(f"Error saving file: {str(e)}")
        return None

def generate_reset_token(user_id):
    """Generate a password reset token."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_reset_token(token):
    """Verify a password reset token."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def validate_password(password):
    """
    Validate password strength.
    Returns (bool, str) tuple - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, ""

def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"

def paginate(query, page, per_page=20):
    """Helper function to paginate SQLAlchemy queries."""
    pagination = query.paginate(page=page, per_page=per_page)
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

def admin_required(f):
    """Decorator to require admin access for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated_function

def partner_required(f):
    """Decorator to require partner access for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_partner():
            if request.is_json:
                return jsonify({'error': 'Partner access required'}), 403
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(requests_per_minute=60):
    """
    Rate limiting decorator.
    Note: This is a simple implementation. For production, use Flask-Limiter or similar.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            ip = request.remote_addr
            
            # Check if IP is in cache and within limits
            # Implementation would go here
            # For now, just pass through
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_activity(action, details=None, level='info'):
    """
    Log user activity with enhanced details.
    
    Args:
        action: The action being performed
        details: Additional details about the action
        level: Log level ('info', 'warning', 'error')
    """
    user_info = (f"User {current_user.username} ({current_user.id})"
                 if current_user.is_authenticated else "Anonymous")
    
    log_message = f"{user_info} performed {action}"
    if details:
        log_message += f" - {details}"
    
    # Add request information
    log_message += f" | IP: {request.remote_addr}"
    log_message += f" | URL: {request.url}"
    log_message += f" | Method: {request.method}"
    
    # Log at appropriate level
    logger = current_app.logger
    if level == 'warning':
        logger.warning(log_message)
    elif level == 'error':
        logger.error(log_message)
    else:
        logger.info(log_message)

def sanitize_filename(filename, max_length=255):
    """
    Sanitize a filename to be safe for the filesystem with enhanced security.
    
    Args:
        filename: The filename to sanitize
        max_length: Maximum allowed filename length
    """
    # Remove any directory components and hidden file indicators
    filename = os.path.basename(filename)
    filename = filename.lstrip('.')
    
    # Remove any non-alphanumeric characters except for periods and hyphens
    filename = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
    
    # Ensure at least one character before extension
    name, ext = os.path.splitext(filename)
    if not name:
        name = 'file'
    
    # Ensure extension is lowercase
    ext = ext.lower()
    
    # Ensure the filename isn't too long
    if len(name) + len(ext) > max_length:
        return name[:max_length-len(ext)] + ext
    
    return name + ext

def get_file_info(filepath):
    """
    Get detailed information about a file.
    
    Returns:
        dict: File information including size, type, dimensions (if image), etc.
    """
    if not os.path.exists(filepath):
        return None
        
    stats = os.stat(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    
    info = {
        'size': stats.st_size,
        'created': datetime.fromtimestamp(stats.st_ctime),
        'modified': datetime.fromtimestamp(stats.st_mtime),
        'extension': ext,
        'mime_type': None,
        'dimensions': None
    }
    
    # Try to determine MIME type
    import mimetypes
    info['mime_type'] = mimetypes.guess_type(filepath)[0]
    
    # Get image dimensions if applicable
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        try:
            with Image.open(filepath) as img:
                info['dimensions'] = img.size
        except:
            pass
            
    return info

def get_file_extension(filename):
    """Get the lowercase file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def get_human_readable_size(size_in_bytes):
    """Convert file size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"

def create_thumbnail(image_path, size=(200, 200)):
    """
    Create a thumbnail for an image file.
    
    Args:
        image_path: Path to the original image
        size: Tuple of (width, height) for thumbnail
        
    Returns:
        str: Path to the thumbnail file
    """
    try:
        thumb_dir = os.path.join(os.path.dirname(image_path), 'thumbnails')
        os.makedirs(thumb_dir, exist_ok=True)
        
        filename = os.path.basename(image_path)
        thumb_path = os.path.join(thumb_dir, f"thumb_{filename}")
        
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumb_path, optimize=True, quality=85)
            
        return thumb_path
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail: {str(e)}")
        return None
