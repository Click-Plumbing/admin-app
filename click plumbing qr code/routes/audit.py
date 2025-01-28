from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app import db, AuditLog, User
from datetime import datetime, timedelta

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit')
@login_required
def log():
    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    days = request.args.get('days', type=int, default=7)
    
    # Base query
    query = AuditLog.query
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action_type:
        query = query.filter(AuditLog.action.like(f'%{action_type}%'))
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.timestamp >= start_date)
    
    # Get results ordered by timestamp
    logs = query.order_by(AuditLog.timestamp.desc()).all()
    users = User.query.all()
    
    return render_template('audit/log.html', logs=logs, users=users)
