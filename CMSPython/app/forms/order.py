from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, IntegerField,
    FloatField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, Optional, NumberRange
)

class OrderForm(FlaskForm):
    """Form for creating and editing orders."""
    # Customer Information
    customer_name = StringField('Customer Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    customer_email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    customer_phone = StringField('Phone', validators=[
        Optional(),
        Length(max=20)
    ])

    # Shipping Information
    shipping_address = TextAreaField('Shipping Address', validators=[
        DataRequired(),
        Length(min=10, max=200)
    ])
    shipping_city = StringField('City', validators=[
        DataRequired(),
        Length(max=100)
    ])
    shipping_state = StringField('State/Province', validators=[
        DataRequired(),
        Length(max=100)
    ])
    shipping_postal_code = StringField('Postal Code', validators=[
        DataRequired(),
        Length(max=20)
    ])
    shipping_country = StringField('Country', validators=[
        DataRequired(),
        Length(max=100)
    ])

    # Order Details
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, message='Quantity must be at least 1')
    ])
    unit_price = FloatField('Unit Price', validators=[
        DataRequired(),
        NumberRange(min=0, message='Price cannot be negative')
    ])
    
    # Status
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])

    # Notes
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500)
    ])

    submit = SubmitField('Submit Order')
