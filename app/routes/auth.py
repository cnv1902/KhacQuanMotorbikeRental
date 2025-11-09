from flask import render_template, request, redirect, url_for, flash, session, make_response, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from . import bp
from ..extensions import get_db_session
from ..models import Accounts


@bp.route('/admin/login', methods=['GET'])
def admin_login_page():
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'session')
    if session.get('account_id'):
        session.clear()
        resp = make_response(render_template('admin/auth-sign-in.html'))
        resp.delete_cookie(cookie_name)
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp

    resp = make_response(render_template('admin/auth-sign-in.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@bp.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    db = get_db_session()
    user = db.query(Accounts).filter(
        (Accounts.username == username) | (Accounts.email == username)
    ).first()

    if not user:
        flash('Tài khoản không tồn tại', 'danger')
        return redirect(url_for('admin.admin_login_page'))

    if not check_password_hash(user.password_hash, password):
        flash('Mật khẩu không đúng', 'danger')
        return redirect(url_for('admin.admin_login_page'))

    session['account_id'] = user.id
    session['account_username'] = user.username
    session['account_full_name'] = user.full_name
    resp = redirect(url_for('admin.admin_index'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@bp.route('/admin/register', methods=['GET'])
def admin_register_page():
    resp = make_response(render_template('admin/auth-sign-up.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@bp.route('/admin/register', methods=['POST'])
def admin_register():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirm_password')
    print(full_name, email, password, confirm)
    if not (email and password and confirm):
        flash('Vui lòng điền đầy đủ thông tin', 'danger')
        return redirect(url_for('admin.admin_register_page'))
    
    if password != confirm:
        flash('Mật khẩu xác nhận không khớp', 'danger')
        return redirect(url_for('admin.admin_register_page'))

    db = get_db_session()
    exists = db.query(Accounts).filter(
        (Accounts.email == email) | (Accounts.username == email)
    ).first()
    if exists:
        flash('Email hoặc username đã tồn tại', 'danger')
        return redirect(url_for('admin.admin_register_page'))

    pwd_hash = generate_password_hash(password)
    new_account = Accounts(username=email, password_hash=pwd_hash, full_name=full_name, email=email)
    db.add(new_account)
    db.commit()
    flash('Đăng ký thành công. Bạn có thể đăng nhập ngay bây giờ.', 'success')
    return redirect(url_for('admin.admin_login_page'))

@bp.route('/admin/logout')
def admin_logout():
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'session')
    session.clear()
    flash('Đã đăng xuất', 'info')
    resp = make_response(render_template('admin/auth-sign-in.html'))
    resp.delete_cookie(cookie_name)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp