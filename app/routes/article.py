from flask import render_template, request, jsonify, redirect, url_for
from sqlalchemy import desc
from datetime import datetime

from . import bp
from ..extensions import get_db_session
from ..models import Article


@bp.route('/tintuc')
def tintuc():
    """Trang tin tức công khai"""
    db = get_db_session()
    try:
        # Lấy danh sách bài viết đã publish, sắp xếp theo ngày mới nhất
        articles = db.query(Article)\
            .filter(Article.is_published == True)\
            .order_by(desc(Article.published_at))\
            .all()
        db.close()
        return render_template('tintuc.html', articles=articles)
    except Exception as e:
        db.close()
        print(f"Error loading articles: {e}")
        return render_template('tintuc.html', articles=[])


@bp.route('/admin/articles')
def articles():
    db = get_db_session()
    try:
        articles = db.query(Article).order_by(desc(Article.created_at)).all()
        db.close()
        return render_template('admin/article.html', articles=articles)
    except Exception as e:
        db.close()
        print(f"Error loading articles: {e}")
        return render_template('admin/article.html', articles=[])

@bp.route('/admin/article/new', methods=['POST'])
def article_create():
    db = get_db_session()
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        featured_image = request.form.get('featured_image')
        is_published = request.form.get('is_published', '0') == '1'
        published_at = request.form.get('published_at')
        view_count = request.form.get('view_count', 0)
        featured_image_file = request.files.get('featured_image_file')

        # Xử lý upload ảnh nếu có
        if featured_image_file and featured_image_file.filename:
            import os
            save_dir = os.path.join('app', 'static', 'images', 'articles')
            os.makedirs(save_dir, exist_ok=True)
            filename = f"{int(datetime.now().timestamp())}_{featured_image_file.filename}"
            filepath = os.path.join(save_dir, filename)
            featured_image_file.save(filepath)
            featured_image = f"images/articles/{filename}"

        article = Article(
            title=title,
            content=content,
            featured_image=featured_image,
            is_published=is_published,
            published_at=datetime.strptime(published_at, "%Y-%m-%d") if published_at else None,
            view_count=int(view_count) if view_count else 0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(article)
        db.commit()
        db.close()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error creating article: {e}")
        return jsonify({"success": False, "message": str(e)})

@bp.route('/admin/article/<int:a_id>/edit', methods=['GET', 'POST'])
def article_edit(a_id):
    db = get_db_session()
    try:
        article = db.query(Article).get(a_id)
        if not article:
            db.close()
            return jsonify({"success": False, "message": "Không tìm thấy bài viết"})
        if request.method == 'GET':
            result = jsonify({"success": True, "article": {
                "id": article.id,
                "title": article.title,
                "content": article.content,
                "featured_image": article.featured_image,
                "is_published": article.is_published,
                "published_at": article.published_at.strftime('%Y-%m-%d') if article.published_at else '',
                "view_count": article.view_count
            }})
            db.close()
            return result
        # POST: cập nhật
        title = request.form.get('title')
        content = request.form.get('content')
        featured_image = request.form.get('featured_image')
        is_published = request.form.get('is_published', '0') == '1'
        published_at = request.form.get('published_at')
        view_count = request.form.get('view_count', 0)
        featured_image_file = request.files.get('featured_image_file')
        if featured_image_file and featured_image_file.filename:
            import os
            save_dir = os.path.join('app', 'static', 'images', 'articles')
            os.makedirs(save_dir, exist_ok=True)
            filename = f"{int(datetime.now().timestamp())}_{featured_image_file.filename}"
            filepath = os.path.join(save_dir, filename)
            featured_image_file.save(filepath)
            featured_image = f"images/articles/{filename}"
        article.title = title
        article.content = content
        article.featured_image = featured_image
        article.is_published = is_published
        article.published_at = datetime.strptime(published_at, "%Y-%m-%d") if published_at else None
        article.view_count = int(view_count) if view_count else 0
        article.updated_at = datetime.now()
        db.commit()
        db.close()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error editing article: {e}")
        return jsonify({"success": False, "message": str(e)})

@bp.route('/admin/article/<int:a_id>/delete', methods=['POST'])
def article_delete(a_id):
    db = get_db_session()
    try:
        article = db.query(Article).get(a_id)
        if not article:
            db.close()
            return jsonify({"success": False, "message": "Không tìm thấy bài viết"})
        db.delete(article)
        db.commit()
        db.close()
        # After deletion, redirect back to the articles list (template expects reload)
        return redirect(url_for('admin.articles'))
    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error deleting article: {e}")
        return jsonify({"success": False, "message": str(e)})
