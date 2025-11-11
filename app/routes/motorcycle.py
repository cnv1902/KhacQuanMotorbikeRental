from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from . import bp
from ..extensions import get_db_session
from ..models import Catagory_Motorcycle, Motorcycles
from decimal import Decimal, InvalidOperation


def _to_decimal(value):
    if value is None or value == '':
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


@bp.route('/admin/catagories_motorcycle')
def catagories_motorcycle():
    db = get_db_session()
    categories = db.query(Catagory_Motorcycle).order_by(Catagory_Motorcycle.id.desc()).all()
    return render_template('admin/catagory-motorcycle.html', motorcycles=categories)


@bp.route('/admin/catagorie_motorcycle/new', methods=['GET', 'POST'])
def catagorie_motorcycle_create():
    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        engine_capacity = request.form.get('engine_capacity')
        price_per_day = _to_decimal(request.form.get('price_per_day'))
        price_per_week = _to_decimal(request.form.get('price_per_week'))
        price_per_month = _to_decimal(request.form.get('price_per_month'))
        
        image = (request.form.get('image') or '').strip()
        
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                subdir = os.path.join('images', 'catagories_motorcycle')
                static_dir = current_app.static_folder
                save_dir = os.path.join(static_dir, subdir)
                os.makedirs(save_dir, exist_ok=True)
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                counter = 1
                final_name = filename
                while os.path.exists(os.path.join(save_dir, final_name)):
                    final_name = f"{base}_{counter}{ext}"
                    counter += 1
                file_path = os.path.join(save_dir, final_name)
                file.save(file_path)
                image = os.path.join(subdir, final_name).replace('\\', '/')

        if not name:
            return jsonify({'success': False, 'message': 'Tên loại xe là bắt buộc'}), 400

        db = get_db_session()
        m = Catagory_Motorcycle(
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
        try:
            print('Saved category', m.id, 'image =', m.image)
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Thêm loại xe thành công'})
    return jsonify({'success': True, 'motorcycle': None})


@bp.route('/admin/catagorie_motorcycle/<int:m_id>/edit', methods=['GET', 'POST'])
def catagorie_motorcycle_edit(m_id):
    db = get_db_session()
    m = db.query(Catagory_Motorcycle).filter_by(id=m_id).first()
    if not m:
        return jsonify({'success': False, 'message': 'Loại xe không tồn tại'}), 404
    if request.method == 'POST':
        previous_image = m.image or ''
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
        new_image = None
        delete_old_image = False
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                subdir = os.path.join('images', 'catagories_motorcycle')
                static_dir = current_app.static_folder
                save_dir = os.path.join(static_dir, subdir)
                os.makedirs(save_dir, exist_ok=True)
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                counter = 1
                final_name = filename
                while os.path.exists(os.path.join(save_dir, final_name)):
                    final_name = f"{base}_{counter}{ext}"
                    counter += 1
                file_path = os.path.join(save_dir, final_name)
                file.save(file_path)
                new_image = os.path.join(subdir, final_name).replace('\\', '/')
                delete_old_image = True 
        if new_image is None:
            image_url = request.form.get('image', '').strip()
            if image_url:
                if image_url != previous_image:
                    new_image = image_url
                    delete_old_image = True
            else:
                if previous_image:
                    delete_old_image = True
                    new_image = None
        if delete_old_image and previous_image:
            try:
                if not previous_image.startswith('http'):
                    old_path = os.path.join(current_app.static_folder, previous_image)
                    if os.path.isfile(old_path):
                        os.remove(old_path)
            except Exception as e:
                print(f"Không thể xóa ảnh cũ trong static: {str(e)}")
        if delete_old_image or new_image is not None:
            m.image = new_image
        db.add(m)
        db.commit()
        try:
            print('Updated category', m.id, 'image =', m.image)
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Cập nhật loại xe thành công'})
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


@bp.route('/admin/catagorie_motorcycle/<int:m_id>/delete', methods=['POST'])
def catagorie_motorcycle_delete(m_id):
    db = get_db_session()
    m = db.query(Catagory_Motorcycle).filter_by(id=m_id).first()
    if not m:
        flash('Loại xe không tồn tại', 'warning')
        return redirect(url_for('admin.catagories_motorcycle'))
    if m.image:
        try:
            if not m.image.startswith('http'):
                old_path = os.path.join(current_app.static_folder, m.image)
                if os.path.isfile(old_path):
                    os.remove(old_path)
            print(f"Đã xóa ảnh trong static: {m.image}")
        except Exception as e:
            print(f"Không thể xóa ảnh trong static: {str(e)}")

    db.delete(m)
    db.commit()
    flash('Xóa loại xe thành công', 'success')
    return redirect(url_for('admin.catagories_motorcycle'))


@bp.route('/admin/motorcycles')
def motorcycles():
    db = get_db_session()
    categories_list = db.query(Catagory_Motorcycle).order_by(Catagory_Motorcycle.name).all()
    motorcycle_id = request.args.get('motorcycle_id', type=int)
    selected_motorcycle = None
    Motorcycles_list = []
    if motorcycle_id:
        selected_motorcycle = db.query(Catagory_Motorcycle).filter_by(id=motorcycle_id).first()
        if selected_motorcycle:
            Motorcycles_list = db.query(Motorcycles).filter_by(
                category_id=motorcycle_id
            ).order_by(Motorcycles.id.desc()).all()
    
    return render_template(
        'admin/motorcycle.html',
        motorcycles=categories_list,
        Motorcycles=Motorcycles_list,
        selected_motorcycle_id=motorcycle_id,
        selected_motorcycle=selected_motorcycle
    )


@bp.route('/admin/motorcycle/new', methods=['GET', 'POST'])
def motorcycle_create():
    if request.method == 'POST':
        motorcycle_id = request.form.get('motorcycle_id')
        license_plate = request.form.get('license_plate')
        model_year = request.form.get('model_year')
        description = request.form.get('description')
        status = request.form.get('status')
        if not motorcycle_id:
            return jsonify({'success': False, 'message': 'Loại xe là bắt buộc'}), 400
        if not license_plate:
            return jsonify({'success': False, 'message': 'Biển số xe là bắt buộc'}), 400
        db = get_db_session()
        existing = db.query(Motorcycles).filter_by(license_plate=license_plate).first()
        if existing:
            return jsonify({'success': False, 'message': 'Biển số xe đã tồn tại'}), 400
        motorcycle = db.query(Catagory_Motorcycle).filter_by(id=motorcycle_id).first()
        if not motorcycle:
            return jsonify({'success': False, 'message': 'Loại xe không tồn tại'}), 400
        model_year_int = None
        if model_year:
            try:
                model_year_int = int(model_year)
            except ValueError:
                pass
        
        dm = Motorcycles(
            category_id=int(motorcycle_id),
            license_plate=license_plate.strip(),
            model_year=model_year_int,
            description=description,
            status=status or 'ready'
        )
        db.add(dm)
        db.commit()
        return jsonify({'success': True, 'message': 'Thêm xe thành công'})
    return jsonify({
        'success': True,
        'motorcycle': {
            'id': dm.id,
            'motorcycle_id': dm.category_id,
            'license_plate': dm.license_plate,
            'model_year': dm.model_year,
            'description': dm.description or '',
            'status': dm.status or 'ready'
        }
    })


@bp.route('/admin/motorcycle/<int:dm_id>/edit', methods=['GET', 'POST'])
def motorcycle_edit(dm_id):
    db = get_db_session()
    dm = db.query(Motorcycles).filter_by(id=dm_id).first()
    if not dm:
        return jsonify({'success': False, 'message': 'Xe không tồn tại'}), 404
    if request.method == 'POST':
        motorcycle_id = request.form.get('motorcycle_id')
        license_plate = request.form.get('license_plate')
        model_year = request.form.get('model_year')
        description = request.form.get('description')
        status = request.form.get('status')
        if not motorcycle_id:
            return jsonify({'success': False, 'message': 'Loại xe là bắt buộc'}), 400
        if not license_plate:
            return jsonify({'success': False, 'message': 'Biển số xe là bắt buộc'}), 400
        existing = db.query(Motorcycles).filter(
            Motorcycles.license_plate == license_plate.strip(),
            Motorcycles.id != dm_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Biển số xe đã tồn tại'}), 400
        motorcycle = db.query(Catagory_Motorcycle).filter_by(id=motorcycle_id).first()
        if not motorcycle:
            return jsonify({'success': False, 'message': 'Loại xe không tồn tại'}), 400
        dm.category_id = int(motorcycle_id)
        dm.license_plate = license_plate.strip()
        if model_year:
            try:
                dm.model_year = int(model_year)
            except ValueError:
                dm.model_year = None
        else:
            dm.model_year = None
        dm.description = description
        dm.status = status or 'ready'
        db.add(dm)
        db.commit()
        return jsonify({'success': True, 'message': 'Cập nhật chi tiết xe thành công'})
    return jsonify({
        'success': True,
        'motorcycle': {
            'id': dm.id,
            'motorcycle_id': dm.category_id,
            'license_plate': dm.license_plate,
            'model_year': dm.model_year,
            'description': dm.description or '',
            'status': dm.status or 'ready'
        }
    })


@bp.route('/admin/motorcycle/<int:dm_id>/delete', methods=['POST'])
def motorcycle_delete(dm_id):
    db = get_db_session()
    dm = db.query(Motorcycles).filter_by(id=dm_id).first()
    if not dm:
        flash('Xe không tồn tại', 'warning')
        return redirect(url_for('admin.motorcycles'))
    motorcycle_id = dm.category_id
    db.delete(dm)
    db.commit()
    flash('Xóa xe thành công', 'success')
    return redirect(url_for('admin.motorcycles', motorcycle_id=motorcycle_id))
