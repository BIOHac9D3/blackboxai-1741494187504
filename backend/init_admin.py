from app import create_app, db
from models.user import User

def init_admin():
    """Initialize the first admin user"""
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print('Admin user already exists')
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_administrator=True
        )
        admin.set_password('admin123')  # Change this in production!
        
        try:
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully')
        except Exception as e:
            db.session.rollback()
            print(f'Error creating admin user: {str(e)}')

if __name__ == '__main__':
    init_admin()
