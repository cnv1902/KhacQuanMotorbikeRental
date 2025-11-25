from dotenv import load_dotenv
import os
import sys
from importlib import import_module

load_dotenv()

# đảm bảo project root trong sys.path
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# chạy bước chuẩn bị (tạo bảng, v.v.)
try:
    import app as app_module
    if hasattr(app_module, 'main'):
        app_module.main()
except Exception as e:
    print("Warning: lỗi khi gọi app.main():", e)

# nếu có Flask app hoặc factory, khởi chạy server dev
flask_app = None
if hasattr(app_module, 'create_app'):
    try:
        flask_app = app_module.create_app()
    except Exception:
        flask_app = None
elif hasattr(app_module, 'app'):
    flask_app = getattr(app_module, 'app')

if flask_app is not None:
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '8000'))
    debug = os.getenv('DEBUG', '1').lower() in ('1', 'true', 'yes')
    print(f"Starting dev server on http://{host}:{port} (debug={debug})")
    flask_app.run(host=host, port=port, debug=debug)
else:
    print("Setup complete. Không tìm thấy web app để chạy tự động.")
    print("Chạy dự án: python runlocal.py")