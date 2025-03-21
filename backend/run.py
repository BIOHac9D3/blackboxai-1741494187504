import os
from app import create_app
from init_db import init_db

if __name__ == '__main__':
    # Initialize environment variables for production
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL') or 'sqlite:///store.db'  # Fallback to SQLite if not set
    
    # Log the DATABASE_URL for debugging
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
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
