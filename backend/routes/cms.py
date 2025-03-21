from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
from models.page import Page
from models.user import User
from forms.cms import (
    PageForm,
    MediaUploadForm,
    CMSSettingsForm,
    NavigationItemForm
)
from app import db
import os
from datetime import datetime

cms_bp = Blueprint('cms', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator:
            flash('You need administrator privileges to access this area.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@cms_bp.route('/cms/dashboard')
@login_required
@admin_required
def dashboard():
    """CMS Dashboard"""
    return render_template('cms/dashboard.html')

@cms_bp.route('/cms/pages')
@login_required
@admin_required
def pages():
    """List all pages"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 10)
    
    query = Page.query
    
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                Page.title.ilike(f'%{search}%'),
                Page.content.ilike(f'%{search}%')
            )
        )
    
    pages = query.order_by(Page.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('cms/pages.html', pages=pages)

@cms_bp.route('/cms/pages/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_page():
    """Create a new page"""
    form = PageForm()
    if form.validate_on_submit():
        page = Page(
            title=form.title.data,
            slug=form.slug.data,
            content=form.content.data,
            meta_description=form.meta_description.data,
            featured_image=form.featured_image.data,
            status=form.status.data,
            template=form.template.data,
            is_visible=form.is_visible.data,
            created_by=current_user.id,
            updated_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        try:
            db.session.add(page)
            db.session.commit()
            flash('Page created successfully.', 'success')
            return redirect(url_for('cms.pages'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating page. Please try again.', 'error')
            current_app.logger.error(f'Error creating page: {str(e)}')
    
    return render_template('cms/edit_page.html', form=form, page=None)

@cms_bp.route('/cms/pages/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_page(id):
    """Edit an existing page"""
    page = Page.query.get_or_404(id)
    form = PageForm(obj=page)
    
    if form.validate_on_submit():
        try:
            page.title = form.title.data
            page.slug = form.slug.data
            page.content = form.content.data
            page.meta_description = form.meta_description.data
            page.featured_image = form.featured_image.data
            page.status = form.status.data
            page.template = form.template.data
            page.is_visible = form.is_visible.data
            page.updated_by = current_user.id
            page.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Page updated successfully.', 'success')
            return redirect(url_for('cms.pages'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating page. Please try again.', 'error')
            current_app.logger.error(f'Error updating page: {str(e)}')
    
    return render_template('cms/edit_page.html', form=form, page=page)

@cms_bp.route('/cms/pages/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_page(id):
    """Delete a page"""
    page = Page.query.get_or_404(id)
    try:
        db.session.delete(page)
        db.session.commit()
        flash('Page deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting page. Please try again.', 'error')
        current_app.logger.error(f'Error deleting page: {str(e)}')
    
    return redirect(url_for('cms.pages'))

@cms_bp.route('/cms/media')
@login_required
@admin_required
def media():
    """Media management"""
    return render_template('cms/media.html')

@cms_bp.route('/cms/media/upload', methods=['POST'])
@login_required
@admin_required
def upload_media():
    """Upload media files"""
    form = MediaUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            try:
                # Save file
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                flash('File uploaded successfully.', 'success')
            except Exception as e:
                flash('Error uploading file. Please try again.', 'error')
                current_app.logger.error(f'Error uploading file: {str(e)}')
    return redirect(url_for('cms.media'))

@cms_bp.route('/cms/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """CMS Settings"""
    form = CMSSettingsForm()
    if form.validate_on_submit():
        try:
            # Save settings
            flash('Settings updated successfully.', 'success')
        except Exception as e:
            flash('Error updating settings. Please try again.', 'error')
            current_app.logger.error(f'Error updating settings: {str(e)}')
    
    return render_template('cms/settings.html', form=form)

@cms_bp.route('/cms/navigation', methods=['GET', 'POST'])
@login_required
@admin_required
def navigation():
    """Navigation management"""
    form = NavigationItemForm()
    if form.validate_on_submit():
        try:
            # Save navigation item
            flash('Navigation item saved successfully.', 'success')
        except Exception as e:
            flash('Error saving navigation item. Please try again.', 'error')
            current_app.logger.error(f'Error saving navigation item: {str(e)}')
    
    return render_template('cms/navigation.html', form=form)
