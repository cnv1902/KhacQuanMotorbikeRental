from dotenv import load_dotenv
import os
import app.models as models

load_dotenv()


def main():
    # create tables then run
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = 'sqlite:///local_dev.db'
    models.create_tables(url=db_url)

if __name__ == '__main__':
    main()
