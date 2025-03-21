from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class OrderForm(FlaskForm):
    user_id = IntegerField('User',
        validators=[DataRequired()]
    )
    
    status = SelectField('Status', 
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled')
        ],
        validators=[DataRequired()]
    )
    
    payment_status = SelectField('Payment Status',
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        validators=[DataRequired()]
    )
    
    shipping_address = TextAreaField('Shipping Address',
        validators=[DataRequired(), Length(max=500)]
    )
    
    billing_address = TextAreaField('Billing Address',
        validators=[DataRequired(), Length(max=500)]
    )
    
    total_amount = FloatField('Total Amount',
        validators=[DataRequired(), NumberRange(min=0)]
    )
    
    payment_id = StringField('Payment ID',
        validators=[Optional(), Length(max=100)]
    )

    # Hidden field for CSRF protection
    csrf_token = HiddenField()

class OrderItemForm(FlaskForm):
    product_id = IntegerField('Product',
        validators=[DataRequired()]
    )
    
    quantity = IntegerField('Quantity',
        validators=[DataRequired(), NumberRange(min=1)]
    )
    
    price = FloatField('Price',
        validators=[DataRequired(), NumberRange(min=0)]
    )
