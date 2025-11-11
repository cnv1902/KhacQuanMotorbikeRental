from flask import Blueprint
from flask import Blueprint, request, redirect, url_for, session
bp = Blueprint('admin', __name__)

@bp.before_request
def ensure_logged_in():
	allowed = {
		'admin.admin_login_page',
		'admin.admin_login',
		'admin.admin_register_page',
		'admin.admin_register',
		'static'
	}
	if request.path.startswith('/admin') and (request.endpoint not in allowed):
		if not session.get('account_id'):
			return redirect(url_for('admin.admin_login_page'))

from . import auth, main, rental, motorcycle, article, info, vnpay, admin_management
