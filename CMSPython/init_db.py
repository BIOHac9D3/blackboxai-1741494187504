from app import create_app, db

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
