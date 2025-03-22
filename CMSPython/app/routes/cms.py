from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Page
from app.forms.cms import PageForm

cms_bp = Blueprint('cms', __name__, url_prefix='/cms')

@cms_bp.route('/')
def index():
    """List all published pages."""
    pages = Page.query.filter_by(published=True).order_by(Page.title).all()
    return render_template('cms/index.html', 
                         title='Content Pages',
                         pages=pages)

@cms_bp.route('/<slug>')
def page(slug):
    """Display a specific page."""
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template(f'cms/{page.template}',
                         title=page.title,
                         page=page)

@cms_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new page."""
    if not current_user.is_administrator:
        flash('You must be an administrator to create pages.', 'error')
        return redirect(url_for('main.index'))
    
    form = PageForm()
    if form.validate_on_submit():
        page = Page(
            title=form.title.data,
            content=form.content.data,
            meta_description=form.meta_description.data,
            template=form.template.data,
            published=form.published.data,
            author_id=current_user.id
        )
        db.session.add(page)
        db.session.commit()
        flash('Page created successfully!', 'success')
        return redirect(url_for('admin.manage_pages'))
    
    return render_template('cms/edit_page.html',
                         title='Create Page',
                         form=form)

@cms_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing page."""
    if not current_user.is_administrator:
        flash('You must be an administrator to edit pages.', 'error')
        return redirect(url_for('main.index'))
    
    page = Page.query.get_or_404(id)
    form = PageForm(obj=page)
    
    if form.validate_on_submit():
        page.title = form.title.data
        page.content = form.content.data
        page.meta_description = form.meta_description.data
        page.template = form.template.data
        page.published = form.published.data
        db.session.commit()
        flash('Page updated successfully!', 'success')
        return redirect(url_for('admin.manage_pages'))
    
    return render_template('cms/edit_page.html',
                         title='Edit Page',
                         form=form,
                         page=page)

@cms_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    """Delete a page."""
    if not current_user.is_administrator:
        flash('You must be an administrator to delete pages.', 'error')
        return redirect(url_for('main.index'))
    
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!', 'success')
    return redirect(url_for('admin.manage_pages'))
