from datetime import datetime

def utility_processor():
    """Add utility variables to template context."""
    return {
        'current_year': datetime.utcnow().year
    }
