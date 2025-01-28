from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Engineer, Account Manager
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    maps_link = db.Column(db.String(500))
    build_date = db.Column(db.Date, nullable=False)
    account_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    part_name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    installation_date = db.Column(db.Date, nullable=False)
    warranty_months = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    last_shutdown = db.Column(db.DateTime)
    flow_rate_1 = db.Column(db.Float)
    flow_rate_2 = db.Column(db.Float)
    pressure_1 = db.Column(db.Float)
    pressure_2 = db.Column(db.Float)
    pressure_3 = db.Column(db.Float)
    temperature_1 = db.Column(db.Float)
    temperature_2 = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
