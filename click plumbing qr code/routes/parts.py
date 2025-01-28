from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db, Part, Machine, log_action
from datetime import datetime
import qrcode
import io
import base64

parts_bp = Blueprint('parts', __name__)

@parts_bp.route('/parts')
@login_required
def list():
    parts = Part.query.all()
    machines = Machine.query.all()
    return render_template('parts/list.html', parts=parts, machines=machines)

@parts_bp.route('/parts/add', methods=['POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            warranty_months = int(request.form['warranty_months'])
            if not (3 <= warranty_months <= 36):
                flash('Warranty must be between 3 and 36 months', 'danger')
                return redirect(url_for('parts.list'))

            part = Part(
                machine_id=request.form['machine_id'],
                part_name=request.form['part_name'],
                serial_number=request.form['serial_number'],
                installation_date=datetime.strptime(request.form['installation_date'], '%Y-%m-%d'),
                warranty_months=warranty_months,
                comments=request.form['comments']
            )
            db.session.add(part)
            db.session.commit()
            log_action(current_user.id, 'Added new part', f'Part ID: {part.id}')
            flash('Part added successfully', 'success')
        except Exception as e:
            flash(f'Error adding part: {str(e)}', 'danger')
            db.session.rollback()
    return redirect(url_for('parts.list'))

@parts_bp.route('/parts/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    part = Part.query.get_or_404(id)
    if request.method == 'POST':
        try:
            warranty_months = int(request.form['warranty_months'])
            if not (3 <= warranty_months <= 36):
                flash('Warranty must be between 3 and 36 months', 'danger')
                return redirect(url_for('parts.list'))

            part.machine_id = request.form['machine_id']
            part.part_name = request.form['part_name']
            part.serial_number = request.form['serial_number']
            part.installation_date = datetime.strptime(request.form['installation_date'], '%Y-%m-%d')
            part.warranty_months = warranty_months
            part.comments = request.form['comments']
            db.session.commit()
            log_action(current_user.id, 'Updated part', f'Part ID: {id}')
            flash('Part updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating part: {str(e)}', 'danger')
            db.session.rollback()
    return redirect(url_for('parts.list'))

@parts_bp.route('/parts/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    part = Part.query.get_or_404(id)
    try:
        db.session.delete(part)
        db.session.commit()
        log_action(current_user.id, 'Deleted part', f'Part ID: {id}')
        flash('Part deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting part: {str(e)}', 'danger')
        db.session.rollback()
    return redirect(url_for('parts.list'))

@parts_bp.route('/parts/<int:id>/qr')
@login_required
def generate_qr(id):
    part = Part.query.get_or_404(id)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"Part ID: {part.id}\nSerial Number: {part.serial_number}\nPart Name: {part.part_name}")
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'qr_code': img_str})
