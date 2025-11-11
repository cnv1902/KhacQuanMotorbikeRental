from flask import render_template, jsonify
from sqlalchemy import desc
from datetime import datetime
from . import bp
from app.extensions import get_db_session
from app.models import StoreInfo, Catagory_Motorcycle, Article


@bp.route('/')
def home():
    session = get_db_session()
    try:
        store_info = session.query(StoreInfo).first()
        motorcycles = session.query(Catagory_Motorcycle).all()
        # Lấy bài viết cuối cùng đã publish
        latest_article = session.query(Article)\
            .filter(Article.is_published == True)\
            .order_by(desc(Article.created_at))\
            .first()
        
        return render_template('index.html', 
                             store_info=store_info,
                             motorcycles=motorcycles,
                             latest_article=latest_article)
    finally:
        session.close()


@bp.route('/admin')
def index():
    return render_template('admin/index.html')


@bp.route('/admin/index')
def admin_index():
    return render_template('admin/index.html')


@bp.route('/health')
@bp.route('/api/health')
@bp.route('/healthcheck')
def health_check():
    """
    Endpoint kiểm tra tình trạng dịch vụ cực nhẹ.
    Không truy vấn DB, không tạo tải.
    Chỉ trả về trạng thái và timestamp.
    """
    return jsonify({
        "status": "ok",
        "service": "KhacQuanMotorbikeRental",
        "timestamp": datetime.utcnow().isoformat()
    }), 200