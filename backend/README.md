# ModernStore Backend

A modern e-commerce backend built with Flask, SQLAlchemy, and other modern Python technologies.

## Features

- User Authentication and Authorization
- Product Management
- Category Management
- Order Processing
- Shopping Cart Functionality
- Admin Dashboard
- RESTful API
- Secure Password Management
- File Upload Handling
- Error Handling
- Rate Limiting
- CSRF Protection

## Tech Stack

- Flask - Web Framework
- SQLAlchemy - ORM
- Flask-Login - User Session Management
- Flask-WTF - Forms and CSRF Protection
- Pillow - Image Processing
- JWT - Token Authentication
- Stripe - Payment Processing
- SQLite/PostgreSQL - Database

## Project Structure

```
backend/
├── models/             # Database models
│   ├── user.py
│   ├── product.py
│   └── order.py
├── routes/            # Route handlers
│   ├── auth.py
│   ├── admin.py
│   └── api.py
├── templates/         # HTML templates
│   ├── admin/
│   ├── auth/
│   └── errors/
├── static/           # Static files
│   ├── css/
│   ├── js/
│   └── uploads/
├── app.py           # Application factory
├── config.py        # Configuration
├── forms.py         # Form definitions
├── utils.py         # Utility functions
├── init_db.py       # Database initialization
└── run.py          # Application entry point
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key
   export DATABASE_URL=sqlite:///store.db
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python run.py
   ```

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `POST /auth/reset-password` - Password reset request

### Products

- `GET /api/products` - List products
- `GET /api/products/<id>` - Get product details
- `POST /api/products` - Create product (Admin only)
- `PUT /api/products/<id>` - Update product (Admin only)
- `DELETE /api/products/<id>` - Delete product (Admin only)

### Categories

- `GET /api/categories` - List categories
- `POST /api/categories` - Create category (Admin only)
- `PUT /api/categories/<id>` - Update category (Admin only)
- `DELETE /api/categories/<id>` - Delete category (Admin only)

### Orders

- `GET /api/orders` - List user's orders
- `POST /api/orders` - Create order
- `GET /api/orders/<id>` - Get order details

### Cart

- `GET /api/cart` - Get cart contents
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/<id>` - Update cart item
- `DELETE /api/cart/<id>` - Remove item from cart

## Admin Dashboard

Access the admin dashboard at `/admin` with the following default credentials:
- Email: admin@modernstore.com
- Password: Admin123!

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

Follow PEP 8 guidelines. Use flake8 for linting:

```bash
flake8 .
```

### Database Migrations

```bash
flask db migrate -m "Migration message"
flask db upgrade
```

## Security

- All passwords are hashed using bcrypt
- CSRF protection enabled for all forms
- Rate limiting on authentication endpoints
- Input validation and sanitization
- Secure file upload handling
- SQL injection prevention through SQLAlchemy
- XSS protection through template escaping

## Production Deployment

1. Update configuration:
   - Set `FLASK_ENV=production`
   - Set secure `SECRET_KEY`
   - Configure production database
   - Set up proper mail server
   - Configure Stripe keys

2. Set up web server (e.g., Gunicorn):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

3. Set up reverse proxy (e.g., Nginx)

4. Enable HTTPS

5. Set up monitoring and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
