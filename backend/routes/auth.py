from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from models.user import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been disabled', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin.dashboard')
        
        flash('Login successful!', 'success')
        return redirect(next_page)
    
    form = LoginForm()
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    if request.is_json:
        return jsonify({'message': 'Logout successful'})
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        
        # Make the first registered user an admin
        if User.query.count() == 0:
            user.role = 'admin'
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'PUT':
        data = request.get_json()
        
        if 'email' in data and data['email'] != current_user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already registered'}), 400
            current_user.email = data['email']
            
        if 'username' in data and data['username'] != current_user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already taken'}), 400
            current_user.username = data['username']
            
        if 'password' in data:
            current_user.set_password(data['password'])
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    
    return render_template('auth/profile.html')

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_request():
    data = request.get_json() if request.is_json else request.form
    email = data.get('email')
    
    user = User.query.filter_by(email=email).first()
    if user:
        # TODO: Implement password reset email functionality
        if request.is_json:
            return jsonify({'message': 'Password reset instructions sent'})
        flash('Check your email for password reset instructions')
    else:
        if request.is_json:
            return jsonify({'error': 'Email not found'}), 404
        flash('Email not found')
    
    return redirect(url_for('auth.login'))
