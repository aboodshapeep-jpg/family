from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Role, ActivityLog, FamilyMember
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = total_users - active_users
    
    # Recent activity
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    # Users by role
    users_by_role = db.session.query(Role.name, db.func.count(User.id)).join(User).group_by(Role.name).all()
    
    # Last 7 days login activity
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_logins = ActivityLog.query.filter(
        ActivityLog.action == 'LOGIN_SUCCESS',
        ActivityLog.timestamp >= seven_days_ago
    ).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'recent_logins': recent_logins,
        'users_by_role': users_by_role
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_logs=recent_logs)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Manage all users"""
    page = request.args.get('page', 1, type=int)
    filter_status = request.args.get('status', 'all')
    filter_role = request.args.get('role', 'all')
    search_query = request.args.get('search', '')
    
    query = User.query
    
    if search_query:
        query = query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%')) |
            (User.first_name.ilike(f'%{search_query}%')) |
            (User.last_name.ilike(f'%{search_query}%'))
        )
    
    if filter_status == 'active':
        query = query.filter_by(is_active=True)
    elif filter_status == 'inactive':
        query = query.filter_by(is_active=False)
    
    if filter_role != 'all':
        role = Role.query.filter_by(name=filter_role).first()
        if role:
            query = query.filter_by(role_id=role.id)
    
    users = query.paginate(page=page, per_page=20)
    roles = Role.query.all()
    
    return render_template('admin/users.html', users=users, roles=roles, 
                         filter_status=filter_status, filter_role=filter_role, 
                         search_query=search_query)

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        user.first_name = request.form.get('first_name', user.first_name)
        user.last_name = request.form.get('last_name', user.last_name)
        user.is_active = request.form.get('is_active') == 'on'
        user.role_id = request.form.get('role_id', user.role_id)
        
        try:
            db.session.commit()
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', user=user, roles=roles)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    if user_id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    username = user.username
    
    try:
        # Delete related records
        ActivityLog.query.filter_by(user_id=user_id).delete()
        ActivityLog.query.filter_by(target_user_id=user_id).delete()
        FamilyMember.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {username} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    """Reset user password"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not new_password or not confirm_password:
        flash('Password fields are required.', 'danger')
    elif new_password != confirm_password:
        flash('Passwords do not match.', 'danger')
    elif len(new_password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
    else:
        user.set_password(new_password)
        db.session.commit()
        flash(f'Password for {user.username} has been reset.', 'success')
    
    return redirect(url_for('admin.edit_user', user_id=user_id))

@admin_bp.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    """View activity logs"""
    page = request.args.get('page', 1, type=int)
    filter_action = request.args.get('action', 'all')
    filter_user = request.args.get('user', '')
    
    query = ActivityLog.query
    
    if filter_action != 'all':
        query = query.filter_by(action=filter_action)
    
    if filter_user:
        query = query.join(User).filter(User.username.ilike(f'%{filter_user}%'))
    
    logs = query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=50)
    
    actions = db.session.query(ActivityLog.action).distinct().all()
    actions = [a[0] for a in actions]
    
    return render_template('admin/activity_logs.html', logs=logs, 
                         filter_action=filter_action, filter_user=filter_user, 
                         actions=actions)

@admin_bp.route('/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user"""
    roles = Role.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role_id = request.form.get('role_id')
        
        # Validation
        if not all([username, email, password, confirm_password, role_id]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            is_active=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html', roles=roles)
