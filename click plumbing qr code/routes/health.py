from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Machine, HealthData
from app import log_action
from datetime import datetime, timedelta

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
@login_required
def dashboard():
    machines = Machine.query.all()
    return render_template('health/dashboard.html', machines=machines)

@health_bp.route('/health/data/<int:machine_id>')
@login_required
def get_machine_data(machine_id):
    # Get the last 24 hours of data
    start_time = datetime.utcnow() - timedelta(hours=24)
    health_data = HealthData.query.filter(
        HealthData.machine_id == machine_id,
        HealthData.timestamp >= start_time
    ).order_by(HealthData.timestamp.asc()).all()
    
    data = {
        'timestamps': [],
        'flow_rate_1': [],
        'flow_rate_2': [],
        'pressure_1': [],
        'pressure_2': [],
        'pressure_3': [],
        'temperature_1': [],
        'temperature_2': [],
        'last_shutdown': None
    }
    
    for record in health_data:
        data['timestamps'].append(record.timestamp.isoformat())
        data['flow_rate_1'].append(record.flow_rate_1)
        data['flow_rate_2'].append(record.flow_rate_2)
        data['pressure_1'].append(record.pressure_1)
        data['pressure_2'].append(record.pressure_2)
        data['pressure_3'].append(record.pressure_3)
        data['temperature_1'].append(record.temperature_1)
        data['temperature_2'].append(record.temperature_2)
        
        if record.last_shutdown:
            data['last_shutdown'] = record.last_shutdown.isoformat()
    
    return jsonify(data)

# API endpoint for receiving health data from machines
@health_bp.route('/api/health/report', methods=['POST'])
def report_health():
    try:
        data = request.get_json()
        machine = Machine.query.filter_by(id=data.get('machine_id')).first()
        
        if not machine:
            return jsonify({'error': 'Machine not found'}), 404
        
        health_data = HealthData(
            machine_id=machine.id,
            flow_rate_1=data.get('flow_rate_1'),
            flow_rate_2=data.get('flow_rate_2'),
            pressure_1=data.get('pressure_1'),
            pressure_2=data.get('pressure_2'),
            pressure_3=data.get('pressure_3'),
            temperature_1=data.get('temperature_1'),
            temperature_2=data.get('temperature_2'),
            last_shutdown=datetime.fromisoformat(data.get('last_shutdown')) if data.get('last_shutdown') else None
        )
        db.session.add(health_data)
        db.session.commit()
        
        log_action(machine.account_manager_id, 'Health data reported', f'Machine {machine.id} reported health data')
        
        return jsonify({'message': 'Health data recorded successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
