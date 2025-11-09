from flask import jsonify
from . import bp


@bp.route('/rental/health')
def rental_health():
    return jsonify({'ok': True, 'service': 'rental'})
