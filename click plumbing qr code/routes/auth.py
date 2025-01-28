from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, User, log_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            log_action(user.id, 'User logged in')
            return redirect(url_for('index'))
        
        flash('Please check your login details and try again.')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log_action(current_user.id, 'User logged out')
    logout_user()
    return redirect(url_for('auth.login'))

# Create default admin user if none exists
def create_default_admin():
    if not User.query.filter_by(email='admin@admin.com').first():
        admin = User(
            email='admin@admin.com',
            password=generate_password_hash('admin123'),
            role='Admin'
        )
        db.session.add(admin)
        db.session.commit()
        log_action(admin.id, 'Default admin user created')
