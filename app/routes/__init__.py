from flask import Blueprint
# Single shared blueprint for the app routes. Grouped route modules will import
# this `bp` and register their routes on it.
from flask import Blueprint, request, redirect, url_for, session
bp = Blueprint('admin', __name__)

# Simple protection: any /admin route (except login/register) requires session
# account_id. If missing, redirect immediately to login page.
@bp.before_request
def ensure_logged_in():
	# allow the login/register endpoints and static files
	allowed = {
		'admin.admin_login_page',
		'admin.admin_login',
		'admin.admin_register_page',
		'admin.admin_register',
		'static'
	}
	# If request is under /admin and not allowed, require login
	if request.path.startswith('/admin') and (request.endpoint not in allowed):
		if not session.get('account_id'):
			return redirect(url_for('admin.admin_login_page'))

# Import submodules so they register routes on the blueprint.
from . import auth, main, rental, motorcycle  # noqa: E402,F401
