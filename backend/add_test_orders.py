from app import create_app, db
from models.user import User
from models.product import Product
from models.order import Order, OrderItem
from datetime import datetime, timedelta
import random

def add_test_orders():
    """Add test orders to the database"""
    app = create_app()
    
    with app.app_context():
        # Create test users if they don't exist
        test_users = [
            ('customer1', 'customer1@example.com'),
            ('customer2', 'customer2@example.com'),
            ('customer3', 'customer3@example.com')
        ]
        
        users = []
        for username, email in test_users:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    username=username,
                    email=email,
                    role='user',
                    is_active=True
                )
                user.set_password('Password123!')
                db.session.add(user)
                db.session.flush()
            users.append(user)
        
        # Get all products
        products = Product.query.all()
        if not products:
            print("No products found. Please run init_db.py first.")
            return
        
        # Create sample orders for the last 30 days
        order_statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled']
        
        for i in range(30):
            # Create 2-5 orders per day
            num_orders = random.randint(2, 5)
            order_date = datetime.utcnow() - timedelta(days=i)
            
            for _ in range(num_orders):
                user = random.choice(users)
                status = random.choice(order_statuses)
                
                # Create order
                order = Order(
                    user_id=user.id,
                    status=status,
                    total_amount=0,  # Will be calculated
                    shipping_address='123 Test St, City, Country',
                    billing_address='123 Test St, City, Country',
                    payment_status='completed' if status in ['paid', 'shipped', 'delivered'] else 'pending',
                    created_at=order_date,
                    updated_at=order_date
                )
                db.session.add(order)
                db.session.flush()  # Get order ID
                
                # Add 1-3 items to order
                num_items = random.randint(1, 3)
                total_amount = 0
                
                for _ in range(num_items):
                    product = random.choice(products)
                    quantity = random.randint(1, 3)
                    price = product.price
                    
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=quantity,
                        price=price
                    )
                    total_amount += price * quantity
                    db.session.add(order_item)
                
                order.total_amount = total_amount
        
        # Commit all changes
        db.session.commit()
        print("Test orders have been added successfully!")

if __name__ == '__main__':
    add_test_orders()
