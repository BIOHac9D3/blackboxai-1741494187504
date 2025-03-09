from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DecimalField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, URL, Optional, NumberRange
from models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    terms = BooleanField('I agree to the Terms of Service', validators=[
        DataRequired(message='You must agree to the terms of service')
    ])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    price = DecimalField('Price', validators=[
        DataRequired(),
        NumberRange(min=0, message='Price must be greater than or equal to 0')
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(),
        NumberRange(min=0, message='Stock must be greater than or equal to 0')
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    is_active = BooleanField('Active')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Category', coerce=int, validators=[Optional()])

class OrderStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ])

class UserProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user and user.id != self.user_id:
            raise ValidationError('Username already in use')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.id != self.user_id:
            raise ValidationError('Email already registered')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class ProductImageForm(FlaskForm):
    image = FileField('Product Image', validators=[DataRequired()])

class UserRoleForm(FlaskForm):
    role = SelectField('Role', choices=[
        ('user', 'User'),
        ('partner', 'Partner'),
        ('admin', 'Admin')
    ])
    is_active = BooleanField('Active')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    min_price = DecimalField('Minimum Price', validators=[Optional()])
    max_price = DecimalField('Maximum Price', validators=[Optional()])
    sort_by = SelectField('Sort By', choices=[
        ('created_at', 'Newest'),
        ('price_asc', 'Price: Low to High'),
        ('price_desc', 'Price: High to Low'),
        ('name', 'Name')
    ])
