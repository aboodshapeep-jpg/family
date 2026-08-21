from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Role, ActivityLog
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def log_activity(action, description=None, target_user_id=None):
    """Log user activity"""
    try:
        log = ActivityLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            description=description,
            target_user_id=target_user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is inactive. Please contact administrator.', 'danger')
                return redirect(url_for('auth.login'))
            
            if not user.is_admin():
                flash('Admin access required.', 'danger')
                log_activity('LOGIN_FAILED', f'Non-admin login attempt: {username}')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=request.form.get('remember_me'))
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_activity('LOGIN_SUCCESS', f'Admin login: {username}')
            flash(f'Welcome back, {user.first_name or user.username}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            log_activity('LOGIN_FAILED', f'Failed login attempt: {username}')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    logout_user()
    log_activity('LOGOUT', f'Admin logout: {username}')
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register-admin', methods=['GET', 'POST'])
def register_admin():
    """Register initial admin account (only once)"""
    admin_role = Role.query.filter_by(name='Admin').first()
    
    # Check if admin already exists
    if User.query.filter_by(role_id=admin_role.id if admin_role else None).first():
        flash('Admin account already exists. Please login.', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register_admin'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register_admin'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('auth.register_admin'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register_admin'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register_admin'))
        
        # Create admin role if it doesn't exist
        if not admin_role:
            admin_role = Role(name='Admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=admin_role.id,
            is_active=True
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        flash('Admin account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_admin.html')
