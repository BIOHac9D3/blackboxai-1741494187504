# CMS Forms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message="Product name is required"),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters")
    ])
    slug = StringField('Slug', validators=[
        DataRequired(message="Slug is required"),
        Length(min=2, max=100, message="Slug must be between 2 and 100 characters")
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message="Description cannot exceed 1000 characters")
    ])
    price = FloatField('Price', validators=[
        DataRequired(message="Price is required"),
        NumberRange(min=0, message="Price must be greater than or equal to 0")
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message="Stock quantity is required"),
        NumberRange(min=0, message="Stock must be greater than or equal to 0")
    ])
    category_id = SelectField('Category', coerce=int, validators=[
        DataRequired(message="Please select a category")
    ])
    image = FileField('Product Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files (JPG, PNG, GIF, WEBP) are allowed!')
    ])
    image_url = StringField('Image URL', validators=[Optional(), URL(message="Please enter a valid URL")])
    is_active = BooleanField('Active', default=True)

class PageForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    meta_description = TextAreaField('Meta Description', validators=[Optional(), Length(max=200)])
    featured_image = StringField('Featured Image URL', validators=[Optional(), URL()])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published')], validators=[DataRequired()])
    template = SelectField('Template', choices=[
        ('default', 'Default'),
        ('full-width', 'Full Width'),
        ('sidebar', 'With Sidebar'),
        ('landing', 'Landing Page')
    ], validators=[DataRequired()])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    is_visible = BooleanField('Visible in Navigation')

class MediaUploadForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=200)])
    caption = TextAreaField('Caption', validators=[Optional(), Length(max=500)])

class CMSSettingsForm(FlaskForm):
    site_title = StringField('Site Title', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description', validators=[Optional(), Length(max=200)])
    logo_url = StringField('Logo URL', validators=[Optional(), URL()])
    favicon_url = StringField('Favicon URL', validators=[Optional(), URL()])
    footer_text = TextAreaField('Footer Text', validators=[Optional(), Length(max=500)])
    analytics_code = TextAreaField('Analytics Code', validators=[Optional()])
    maintenance_mode = BooleanField('Maintenance Mode')

class NavigationItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=50)])
    url = StringField('URL', validators=[DataRequired(), Length(max=200)])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)])
    parent_id = SelectField('Parent Item', coerce=int, validators=[Optional()])
    is_visible = BooleanField('Visible')
