import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from app import create_app, db
from app.models import User, Category, Product, Page, Order, OrderItem

app = create_app()

if __name__ == '__main__':
    # Get port from command line arguments
    port = 5000
    if '--port' in sys.argv:
        try:
            port_index = sys.argv.index('--port') + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])
        except (ValueError, IndexError):
            print("Invalid port number, using default port 5000")
    
    # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/cms.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('CMS startup')
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)
