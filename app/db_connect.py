import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
USER = os.getenv("user") or os.getenv("DB_USER") or os.getenv("DB_USERNAME")
PASSWORD = os.getenv("password") or os.getenv("DB_PASSWORD")
HOST = os.getenv("host") or os.getenv("DB_HOST")
PORT = os.getenv("port") or os.getenv("DB_PORT")
DBNAME = os.getenv("dbname") or os.getenv("DB_DATABASE")

def try_connect():
    try:
        if DATABASE_URL:
            print("Sử dụng DATABASE_URL:", DATABASE_URL.split("@")[0] + "@...")
            conn = psycopg2.connect(DATABASE_URL)
        else:
            print("Sử dụng các biến riêng lẻ:")
            print(f" host={HOST} port={PORT} user={USER} dbname={DBNAME}")
            conn = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            )

        print("Kết nối thành công")
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        print("Current Time:", cur.fetchone())
        cur.close()
        conn.close()
        print("Đóng kết nối")

    except Exception as e:
        print("Failed to connect:", e)


if __name__ == "__main__":
    try_connect()
