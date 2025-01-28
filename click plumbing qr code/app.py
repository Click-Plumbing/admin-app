from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import qrcode
from io import BytesIO
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/clickplumbing.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Import models after db initialization to avoid circular imports
from models import User, Machine, Part, AuditLog

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_action(user_id, action, details=None):
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

@app.route('/')
@login_required
def index():
    total_machines = Machine.query.count()
    total_parts = Part.query.count()
    total_users = User.query.count()
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    # Get parts with warranties expiring in the next 30 days
    today = datetime.now().date()
    thirty_days = today + timedelta(days=30)
    expiring_parts = []
    all_parts = Part.query.all()
    
    for part in all_parts:
        warranty_end = part.installation_date + timedelta(days=part.warranty_months * 30)
        if today <= warranty_end <= thirty_days:
            expiring_parts.append({
                'name': part.part_name,
                'serial': part.serial_number,
                'expiry': warranty_end
            })
    
    return render_template('index.html',
                         total_machines=total_machines,
                         total_parts=total_parts,
                         total_users=total_users,
                         recent_activity=recent_activity,
                         expiring_parts=expiring_parts)

# Routes will be implemented in separate files
from routes.auth import auth_bp, create_default_admin
from routes.machines import machines_bp
from routes.parts import parts_bp
from routes.health import health_bp
from routes.users import users_bp
from routes.audit import audit_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(machines_bp)
app.register_blueprint(parts_bp)
app.register_blueprint(health_bp)
app.register_blueprint(users_bp)
app.register_blueprint(audit_bp)

# Initialize Admin
admin = Admin(app, name='Click Plumbing Admin', template_mode='bootstrap3')
admin.add_view(ModelView(Machine, db.session))
admin.add_view(ModelView(Part, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(AuditLog, db.session))

# Create database and default admin user
with app.app_context():
    db.create_all()
    create_default_admin()

if __name__ == '__main__':
    app.run(debug=True)
