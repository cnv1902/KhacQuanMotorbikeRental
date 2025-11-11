from dotenv import load_dotenv
import os
import app.models as models

load_dotenv()

# Initialize database tables
db_url = os.getenv('DATABASE_URL')
if not db_url:
    db_url = 'sqlite:///local_dev.db'
models.create_tables(url=db_url)

# Create Flask app instance for gunicorn
from app import create_app
app = create_app()


def main():
    """Run the app in development mode."""
    app.run(debug=True)


if __name__ == '__main__':
    main()
