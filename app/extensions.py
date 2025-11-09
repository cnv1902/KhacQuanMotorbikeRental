import os
from sqlalchemy.orm import sessionmaker
import app.models as models


def get_db_session():
    db_url = os.getenv('DATABASE_URL') or os.getenv('DATABASE_URL_LOCAL')
    if not db_url:
        db_url = 'sqlite:///local_dev.db'
    engine = models.create_tables(url=db_url)
    Session = sessionmaker(bind=engine)
    return Session()
