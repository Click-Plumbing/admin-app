from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db, Machine, User, log_action
from datetime import datetime

machines_bp = Blueprint('machines', __name__)

@machines_bp.route('/machines')
@login_required
def list():
    machines = Machine.query.all()
    account_managers = User.query.filter_by(role='Account Manager').all()
    return render_template('machines/list.html', machines=machines, account_managers=account_managers)

@machines_bp.route('/machines/add', methods=['POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            machine = Machine(
                customer_name=request.form['customer_name'],
                location_name=request.form['location_name'],
                maps_link=request.form['maps_link'],
                build_date=datetime.strptime(request.form['build_date'], '%Y-%m-%d'),
                account_manager_id=request.form.get('account_manager_id')
            )
            db.session.add(machine)
            db.session.commit()
            log_action(current_user.id, 'Added new machine', f'Machine ID: {machine.id}')
            flash('Machine added successfully', 'success')
        except Exception as e:
            flash(f'Error adding machine: {str(e)}', 'danger')
            db.session.rollback()
    return redirect(url_for('machines.list'))

@machines_bp.route('/machines/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    machine = Machine.query.get_or_404(id)
    if request.method == 'POST':
        try:
            machine.customer_name = request.form['customer_name']
            machine.location_name = request.form['location_name']
            machine.maps_link = request.form['maps_link']
            machine.build_date = datetime.strptime(request.form['build_date'], '%Y-%m-%d')
            machine.account_manager_id = request.form.get('account_manager_id')
            db.session.commit()
            log_action(current_user.id, 'Updated machine', f'Machine ID: {id}')
            flash('Machine updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating machine: {str(e)}', 'danger')
            db.session.rollback()
    return redirect(url_for('machines.list'))

@machines_bp.route('/machines/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if current_user.role != 'Admin':
        flash('Only administrators can delete machines', 'danger')
        return redirect(url_for('machines.list'))
    
    machine = Machine.query.get_or_404(id)
    try:
        db.session.delete(machine)
        db.session.commit()
        log_action(current_user.id, 'Deleted machine', f'Machine ID: {id}')
        flash('Machine deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting machine: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('machines.list'))
