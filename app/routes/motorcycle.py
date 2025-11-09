from flask import render_template, request, redirect, url_for, flash, jsonify
from . import bp
from ..extensions import get_db_session
from ..models import Motorcycle
from decimal import Decimal, InvalidOperation
import os
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def get_upload_folder():
    """Get the upload folder path"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    upload_folder = os.path.join(base_dir, 'app', 'static', 'images', 'motorcycles')
    return upload_folder

def _to_decimal(value):
    if value is None or value == '':
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save uploaded file and return the URL path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # Ensure upload directory exists
        upload_folder = get_upload_folder()
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Return URL path relative to static folder
        return f"images/motorcycles/{filename}"
    return None


@bp.route('/admin/motorcycles')
def motorcycles():
    db = get_db_session()
    motorcycles_list = db.query(Motorcycle).order_by(Motorcycle.id.desc()).all()
    return render_template('admin/motorcycle.html', motorcycles=motorcycles_list)


@bp.route('/admin/motorcycles/new', methods=['GET', 'POST'])
def motorcycle_create():
    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        engine_capacity = request.form.get('engine_capacity')
        price_per_day = _to_decimal(request.form.get('price_per_day'))
        price_per_week = _to_decimal(request.form.get('price_per_week'))
        price_per_month = _to_decimal(request.form.get('price_per_month'))
        
        # Handle image upload
        image = request.form.get('image')  # URL input
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename:
                uploaded_path = save_uploaded_file(file)
                if uploaded_path:
                    image = uploaded_path

        if not name:
            return jsonify({'success': False, 'message': 'Tên xe là bắt buộc'}), 400

        db = get_db_session()
        m = Motorcycle(
            name=name,
            brand=brand,
            engine_capacity=engine_capacity,
            price_per_day=price_per_day,
            price_per_week=price_per_week,
            price_per_month=price_per_month,
            image=image,
        )
        db.add(m)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Thêm xe thành công'})

    # GET request - return JSON for modal
    return jsonify({'success': True, 'motorcycle': None})


@bp.route('/admin/motorcycles/<int:m_id>/edit', methods=['GET', 'POST'])
def motorcycle_edit(m_id):
    db = get_db_session()
    m = db.query(Motorcycle).filter_by(id=m_id).first()
    if not m:
        return jsonify({'success': False, 'message': 'Xe không tồn tại'}), 404

    if request.method == 'POST':
        m.name = request.form.get('name') or m.name
        m.brand = request.form.get('brand') or m.brand
        m.engine_capacity = request.form.get('engine_capacity') or m.engine_capacity
        price_per_day = _to_decimal(request.form.get('price_per_day'))
        price_per_week = _to_decimal(request.form.get('price_per_week'))
        price_per_month = _to_decimal(request.form.get('price_per_month'))
        if price_per_day is not None:
            m.price_per_day = price_per_day
        if price_per_week is not None:
            m.price_per_week = price_per_week
        if price_per_month is not None:
            m.price_per_month = price_per_month
        
        # Handle image upload
        image = request.form.get('image')  # URL input
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename:
                uploaded_path = save_uploaded_file(file)
                if uploaded_path:
                    image = uploaded_path
        
        if image:
            m.image = image

        db.add(m)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Cập nhật xe thành công'})

    # GET request - return JSON for modal
    return jsonify({
        'success': True,
        'motorcycle': {
            'id': m.id,
            'name': m.name,
            'brand': m.brand or '',
            'engine_capacity': m.engine_capacity or '',
            'price_per_day': str(m.price_per_day) if m.price_per_day else '',
            'price_per_week': str(m.price_per_week) if m.price_per_week else '',
            'price_per_month': str(m.price_per_month) if m.price_per_month else '',
            'image': m.image or ''
        }
    })


@bp.route('/admin/motorcycles/<int:m_id>/delete', methods=['POST'])
def motorcycle_delete(m_id):
    db = get_db_session()
    m = db.query(Motorcycle).filter_by(id=m_id).first()
    if not m:
        flash('Xe không tồn tại', 'warning')
        return redirect(url_for('admin.admin_index'))

    db.delete(m)
    db.commit()
    flash('Xóa xe thành công', 'success')
    return redirect(url_for('admin.admin_index'))
