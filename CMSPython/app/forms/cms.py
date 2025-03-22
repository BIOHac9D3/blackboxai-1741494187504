from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, URL
from app.models.page import Page

class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Save Category')

class ProductForm(FlaskForm):
    """Form for creating and editing products."""
    name = StringField('Product Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, max=2000)
    ])
    price = FloatField('Price', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Product Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Product')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        from app.models import Category
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name')]

class PageForm(FlaskForm):
    """Form for creating and editing pages."""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    content = TextAreaField('Content')
    meta_description = TextAreaField('Meta Description', validators=[
        Optional(),
        Length(max=160)
    ])
    template = SelectField('Template', choices=[])
    published = BooleanField('Published')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.template.choices = [(t['file'], t['name']) for t in Page.get_templates()]

class MediaUploadForm(FlaskForm):
    """Form for uploading media files."""
    file = FileField('File', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'], 'Invalid file type')
    ])
    submit = SubmitField('Upload')
