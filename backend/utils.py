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

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder='products'):
    """Save an image file and return its path."""
    if not file or not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(filename)
    
    # Create folder if it doesn't exist
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(folder_path, exist_ok=True)
    
    filepath = os.path.join(folder_path, unique_filename)
    
    # Save and optimize image
    try:
        image = Image.open(file)
        image.thumbnail((800, 800))  # Resize if too large
        image.save(filepath, optimize=True, quality=85)
        return f"/static/uploads/{folder}/{unique_filename}"
    except Exception as e:
        current_app.logger.error(f"Error saving image: {str(e)}")
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

def log_activity(action, details=None):
    """Log user activity."""
    # Implementation would go here
    # For now, just log to app logger
    current_app.logger.info(
        f"User {current_user.id if current_user.is_authenticated else 'Anonymous'} "
        f"performed {action} - {details or ''}"
    )

def sanitize_filename(filename):
    """Sanitize a filename to be safe for the filesystem."""
    # Remove any directory components
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except for periods and hyphens
    filename = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
    
    # Ensure the filename isn't too long
    max_length = 255
    name, ext = os.path.splitext(filename)
    if len(filename) > max_length:
        return name[:max_length-len(ext)] + ext
    
    return filename

def get_file_extension(filename):
    """Get the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()
