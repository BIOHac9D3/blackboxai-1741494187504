from app import create_app, db
from app.models import Category, Product
from datetime import datetime

def add_test_data():
    app = create_app()
    with app.app_context():
        # Clear existing data
        Product.query.delete()
        Category.query.delete()
        db.session.commit()

        # Create categories
        electronics = Category(name='Electronics', description='Electronic devices and gadgets')
        books = Category(name='Books', description='Physical and digital books')
        clothing = Category(name='Clothing', description='Men\'s and women\'s clothing')

        db.session.add_all([electronics, books, clothing])
        db.session.commit()

        # Create products
        products = [
            # Electronics
            Product(
                name='Smartphone X',
                description='Latest smartphone with amazing features',
                price=999.99,
                stock=50,
                category=electronics,
                is_active=True,
                is_featured=True
            ),
            Product(
                name='Laptop Pro',
                description='Professional laptop for developers',
                price=1499.99,
                stock=30,
                category=electronics,
                is_active=True
            ),
            # Books
            Product(
                name='Python Programming',
                description='Learn Python programming from scratch',
                price=39.99,
                stock=100,
                category=books,
                is_active=True,
                is_featured=True
            ),
            Product(
                name='Web Development Guide',
                description='Complete guide to modern web development',
                price=49.99,
                stock=75,
                category=books,
                is_active=True
            ),
            # Clothing
            Product(
                name='Classic T-Shirt',
                description='Comfortable cotton t-shirt',
                price=19.99,
                stock=200,
                category=clothing,
                is_active=True,
                is_featured=True
            ),
            Product(
                name='Denim Jeans',
                description='Classic blue denim jeans',
                price=59.99,
                stock=150,
                category=clothing,
                is_active=True
            )
        ]

        for product in products:
            db.session.add(product)

        db.session.commit()
        print("Test data added successfully!")

if __name__ == '__main__':
    add_test_data()
