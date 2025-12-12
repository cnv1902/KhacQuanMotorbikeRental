"""Script để kiểm tra và insert dữ liệu test vào database."""

import os
from dotenv import load_dotenv
from app.extensions import get_db_session
from app.models import StoreInfo, Catagory_Motorcycle, Article, create_tables
from datetime import datetime

load_dotenv()

def check_and_seed_data():
    """Kiểm tra và insert dữ liệu test nếu database trống."""
    
    # Tạo tables nếu chưa có
    db_url = os.getenv('DATABASE_URL') or os.getenv('DATABASE_URL_LOCAL')
    if not db_url:
        print("❌ Không tìm thấy DATABASE_URL trong .env")
        return
    
    print(f"✅ Đang kết nối đến database...")
    engine = create_tables(url=db_url)
    print("✅ Tables đã được tạo (nếu chưa tồn tại)")
    
    session = get_db_session()
    
    try:
        # Kiểm tra StoreInfo
        store_count = session.query(StoreInfo).count()
        print(f"\n📊 Số lượng StoreInfo: {store_count}")
        
        if store_count == 0:
            print("➕ Thêm dữ liệu test cho StoreInfo...")
            store = StoreInfo(
                store_name="Cho thuê xe máy Anh Khánh",
                owner_name="Anh Khánh",
                address="K25 Trương Định, Quận Sơn Trà, Đà Nẵng, Vietnam, 55000",
                phone="0123456789",
                email="contact@anhkhanh.com",
                business_hours="8:00 AM - 8:00 PM",
                google_map_url="https://maps.google.com",
                slide_url="",
                description="Dịch vụ cho thuê xe máy uy tín tại Đà Nẵng"
            )
            session.add(store)
            session.commit()
            print("✅ Đã thêm StoreInfo")
        else:
            store = session.query(StoreInfo).first()
            print(f"   Tên cửa hàng: {store.store_name}")
        
        # Kiểm tra Motorcycles
        moto_count = session.query(Catagory_Motorcycle).count()
        print(f"\n📊 Số lượng Motorcycles: {moto_count}")
        
        if moto_count == 0:
            print("➕ Thêm dữ liệu test cho Motorcycles...")
            motorcycles = [
                Catagory_Motorcycle(
                    name="Honda Wave Alpha",
                    category_id=1,
                    brand="Honda",
                    engine_capacity="110cc",
                    price_per_day=100000,
                    price_per_week=600000,
                    image_url="",
                    description="Xe số tiết kiệm nhiên liệu",
                    is_available=True
                ),
                Catagory_Motorcycle(
                    name="Yamaha Exciter 155",
                    category_id=2,
                    brand="Yamaha",
                    engine_capacity="155cc",
                    price_per_day=150000,
                    price_per_week=900000,
                    image_url="",
                    description="Xe côn tay thể thao",
                    is_available=True
                ),
                Catagory_Motorcycle(
                    name="Honda Vision",
                    category_id=3,
                    brand="Honda",
                    engine_capacity="110cc",
                    price_per_day=120000,
                    price_per_week=700000,
                    image_url="",
                    description="Xe tay ga đa dạng màu sắc",
                    is_available=True
                ),
            ]
            for moto in motorcycles:
                session.add(moto)
            session.commit()
            print(f"✅ Đã thêm {len(motorcycles)} xe mẫu")
        else:
            print("   Danh sách xe:")
            for moto in session.query(Catagory_Motorcycle).limit(5).all():
                print(f"   - {moto.name} ({moto.brand}) - {moto.price_per_day:,}đ/ngày")
        
        # Kiểm tra Articles
        article_count = session.query(Article).count()
        print(f"\n📊 Số lượng Articles: {article_count}")
        
        if article_count == 0:
            print("➕ Thêm dữ liệu test cho Articles...")
            articles = [
                Article(
                    title="Hướng dẫn thuê xe máy tại Đà Nẵng",
                    content="Nội dung chi tiết về cách thuê xe máy...",
                    featured_image="",
                    is_published=True,
                    view_count=0,
                    published_at=datetime.now()
                ),
                Article(
                    title="Bảng giá thuê xe máy mới nhất 2024",
                    content="Cập nhật bảng giá thuê xe...",
                    featured_image="",
                    is_published=True,
                    view_count=0,
                    published_at=datetime.now()
                ),
            ]
            for article in articles:
                session.add(article)
            session.commit()
            print(f"✅ Đã thêm {len(articles)} bài viết")
        else:
            print("   Danh sách bài viết:")
            for article in session.query(Article).limit(5).all():
                status = "✓ Published" if article.is_published else "✗ Draft"
                print(f"   - {article.title} [{status}]")
        
        print("\n" + "="*60)
        print("✅ HOÀN TẤT! Database đã có dữ liệu.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    check_and_seed_data()
