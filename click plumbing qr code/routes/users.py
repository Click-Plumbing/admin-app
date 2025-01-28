from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db, User, log_action

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@login_required
def list():
    if current_user.role != 'Admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('users/list.html', users=users)

@users_bp.route('/users/add', methods=['POST'])
@login_required
def add():
    if current_user.role != 'Admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Check if user already exists
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('users.list'))

            # Validate role
            role = request.form['role']
            if role not in ['Admin', 'Engineer', 'Account Manager']:
                flash('Invalid role selected', 'danger')
                return redirect(url_for('users.list'))

            user = User(
                email=request.form['email'],
                password=generate_password_hash(request.form['password']),
                role=role
            )
            db.session.add(user)
            db.session.commit()
            log_action(current_user.id, 'Added new user', f'User: {user.email}, Role: {user.role}')
            flash('User added successfully', 'success')
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'danger')
            db.session.rollback()
    return redirect(url_for('users.list'))

@users_bp.route('/users/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    if current_user.role != 'Admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Prevent changing own role
            if user.id == current_user.id and user.role != request.form['role']:
                flash('Cannot change your own role', 'danger')
                return redirect(url_for('users.list'))

            # Validate role
            role = request.form['role']
            if role not in ['Admin', 'Engineer', 'Account Manager']:
                flash('Invalid role selected', 'danger')
                return redirect(url_for('users.list'))

            user.email = request.form['email']
            if request.form['password']:
                user.password = generate_password_hash(request.form['password'])
            user.role = role
            db.session.commit()
            log_action(current_user.id, 'Updated user', f'User: {user.email}, Role: {user.role}')
            flash('User updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'danger')
            db.session.rollback()
    return redirect(url_for('users.list'))

@users_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'Admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    if id == current_user.id:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('users.list'))
    
    user = User.query.get_or_404(id)
    try:
        log_action(current_user.id, 'Deleted user', f'User: {user.email}, Role: {user.role}')
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('users.list'))
