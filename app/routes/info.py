from flask import render_template, request, redirect, url_for, flash
import re
from . import bp
from app.extensions import get_db_session
from app.models import StoreInfo


def convert_google_drive_link(url):
    """
    Chuyển đổi Google Drive link thành direct link để hiển thị ảnh.
    
    Các định dạng được hỗ trợ:
    - https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/uc?id=FILE_ID
    
    Trả về: https://lh3.googleusercontent.com/d/FILE_ID (Google User Content - hoạt động tốt hơn)
    Hoặc: https://drive.google.com/thumbnail?id=FILE_ID&sz=w2000 (Thumbnail với kích thước lớn)
    """
    if not url:
        return url
    
    # Nếu không phải Google Drive link, trả về nguyên URL
    if 'drive.google.com' not in url:
        return url
    
    # Nếu đã là direct link từ googleusercontent hoặc thumbnail, trả về luôn
    if 'googleusercontent.com' in url or 'drive.google.com/thumbnail' in url:
        return url
    
    # Pattern 1: https://drive.google.com/file/d/FILE_ID/view
    pattern1 = r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)'
    match1 = re.search(pattern1, url)
    if match1:
        file_id = match1.group(1)
        # Sử dụng Google User Content - ổn định hơn cho việc nhúng ảnh
        return f'https://lh3.googleusercontent.com/d/{file_id}'
    
    # Pattern 2: https://drive.google.com/open?id=FILE_ID
    pattern2 = r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)'
    match2 = re.search(pattern2, url)
    if match2:
        file_id = match2.group(1)
        return f'https://lh3.googleusercontent.com/d/{file_id}'
    
    # Pattern 3: https://drive.google.com/uc?export=view&id=FILE_ID
    pattern3 = r'[?&]id=([a-zA-Z0-9_-]+)'
    match3 = re.search(pattern3, url)
    if match3:
        file_id = match3.group(1)
        return f'https://lh3.googleusercontent.com/d/{file_id}'
    
    # Nếu không match pattern nào, trả về URL gốc
    return url


@bp.route('/admin/store-info', methods=['GET', 'POST'])
def store_info():
    session = get_db_session()
    store = session.query(StoreInfo).first()
    if request.method == 'POST':
        if not store:
            store = StoreInfo()
            session.add(store)
        store.store_name = request.form.get('store_name')
        store.owner_name = request.form.get('owner_name')
        store.address = request.form.get('address')
        store.phone = request.form.get('phone')
        store.email = request.form.get('email')
        store.business_hours = request.form.get('business_hours')
        store.google_map_url = request.form.get('google_map_url')
        
        # Xử lý chuyển đổi Google Drive link sang direct link
        slide_url = request.form.get('slide_url')
        if slide_url:
            slide_url = convert_google_drive_link(slide_url)
        store.slide_url = slide_url
        
        store.description = request.form.get('description')
        session.commit()
        flash('Cập nhật thông tin cửa hàng thành công!', 'success')
        session.close()
        return redirect(url_for('admin.store_info'))
    result = render_template('admin/store_info.html', store=store)
    session.close()
    return result