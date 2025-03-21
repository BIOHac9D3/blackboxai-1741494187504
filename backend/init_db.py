import os
from app import create_app, db
from models.user import User
from models.product import Category, Product
from datetime import datetime

def init_db():
    """Initialize the database with some sample data."""
    app = create_app()  # Ensure the app is created with the correct context
    if not os.environ.get('DATABASE_URL'):
        raise ValueError("DATABASE_URL is not set. Please set it in your environment.")
    
    with app.app_context():
        print(f"Using DATABASE_URL: {os.environ.get('DATABASE_URL')}")
        # Create tables
        db.create_all()
        
            # Check if admin user exists
            admin = User.query.filter_by(email='admin@modernstore.com').first()
            if not admin:
                # Create admin user
                admin = User(
                    username='admin',
                    email='admin@modernstore.com',
                    is_administrator=True,
                    is_active=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
            else:
                print("Admin user already exists.")
            
            # Create sample categories if they do not exist
            categories_data = [
                {'name': 'Electronics', 'slug': 'electronics'},
                {'name': 'Fashion', 'slug': 'fashion'},
                {'name': 'Home & Living', 'slug': 'home-living'},
                {'name': 'Sports', 'slug': 'sports'}
            ]
            for category_data in categories_data:
                if not Category.query.filter_by(slug=category_data['slug']).first():
                    category = Category(**category_data)
                    db.session.add(category)
            
            # Commit to get category IDs
            db.session.commit()
            
            # Create sample products
            products = [
                {
                    'name': 'Premium Laptop',
                    'slug': 'premium-laptop',
                    'description': 'High performance laptop for professionals',
                    'price': 999.99,
                    'stock': 50,
                    'category_id': categories[0].id,
                    'image_url': None,
                    'is_active': True
                },
                {
                    'name': 'Wireless Headphones',
                    'slug': 'wireless-headphones',
                    'description': 'Premium sound quality headphones',
                    'price': 199.99,
                    'stock': 100,
                    'category_id': categories[0].id,
                    'image_url': None,
                    'is_active': True
                },
                {
                    'name': 'Designer T-Shirt',
                    'slug': 'designer-t-shirt',
                    'description': 'Comfortable and stylish t-shirt',
                    'price': 29.99,
                    'stock': 200,
                    'category_id': categories[1].id,
                    'image_url': None,
                    'is_active': True
                },
                {
                    'name': 'Smart Watch',
                    'slug': 'smart-watch',
                    'description': 'Track your fitness and stay connected',
                    'price': 299.99,
                    'stock': 75,
                    'category_id': categories[0].id,
                    'image_url': None,
                    'is_active': True
                }
            ]
            
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            
            # Commit all changes
            db.session.commit()
            
            print("Database initialized with sample data!")
            print("Admin user created:")
            print("Email: admin@modernstore.com")
            print("Password: Admin123!")
        else:
            print("Database already initialized!")

if __name__ == '__main__':
    init_db()
