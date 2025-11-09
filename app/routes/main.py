from flask import render_template
from . import bp


@bp.route('/admin')
def index():
    return render_template('admin/index.html')


@bp.route('/admin/index')
def admin_index():
    return render_template('admin/index.html')
