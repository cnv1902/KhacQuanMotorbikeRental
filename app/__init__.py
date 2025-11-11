from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    """Create and configure the Flask app.

    - Loads environment via .env
    - Sets secret key
    - Registers routes from the `app.routes` package
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    
    # Tăng kích thước tối đa cho upload file và request body
    # Mặc định Flask là 16MB, tăng lên 50MB để cho phép upload ảnh lớn và nội dung bài viết dài
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

    # Register routes
    from .routes import bp
    app.register_blueprint(bp)

    return app
