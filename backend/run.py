import os
from app import create_app
from init_db import init_db

if __name__ == '__main__':
    # Initialize environment variables if needed
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Create the Flask application
    app = create_app()
    
    # Initialize the database with sample data
    with app.app_context():
        init_db()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',  # Make server publicly available
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
