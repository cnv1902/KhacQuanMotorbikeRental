# 🏍️ Hệ Thống Quản Lý Cho Thuê Xe Máy - KhacQuanMotorbikeRental

## 📋 Mục Lục
- [Tổng Quan Hệ Thống](#-tổng-quan-hệ-thống)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Cấu Trúc Thư Mục Chi Tiết](#-cấu-trúc-thư-mục-chi-tiết)
- [Luồng Hoạt Động Hệ Thống](#-luồng-hoạt-động-hệ-thống)
- [Mô Hình Dữ Liệu](#-mô-hình-dữ-liệu)
- [Hướng Dẫn Cài Đặt](#-hướng-dẫn-cài-đặt)
- [Các Thuật Ngữ Quan Trọng](#-các-thuật-ngữ-quan-trọng)

---

## 🎯 Tổng Quan Hệ Thống

**KhacQuanMotorbikeRental** là hệ thống quản lý cho thuê xe máy toàn diện, được xây dựng bằng **Flask Framework** (Python), tích hợp thanh toán **VNPay** và quản lý database với **PostgreSQL/SQLAlchemy**.

### Tính Năng Chính:
✅ **Quản lý xe máy**: Danh mục xe, chi tiết xe, trạng thái xe  
✅ **Quản lý khách hàng**: Thông tin cá nhân, CCCD, giấy phép lái xe  
✅ **Đặt xe trực tuyến**: Form đặt xe, chọn ngày, tính giá tự động  
✅ **Thanh toán VNPay**: Tích hợp cổng thanh toán trực tuyến  
✅ **Quản trị viên**: Dashboard quản lý đơn hàng, bài viết, thông tin cửa hàng  
✅ **Bài viết tin tức**: Quản lý nội dung marketing

---

## 🛠️ Công Nghệ Sử Dụng

| Công nghệ | Phiên bản | Mục đích |
|-----------|-----------|----------|
| **Python** | 3.x | Ngôn ngữ lập trình chính |
| **Flask** | 2.3.3 | Web framework (xử lý HTTP requests/responses) |
| **SQLAlchemy** | 2.0.23 | ORM - Quản lý database bằng Python objects |
| **PostgreSQL** | - | Database quan hệ lưu trữ dữ liệu |
| **Gunicorn** | 21.2.0 | WSGI server cho production |
| **VNPay SDK** | Custom | Tích hợp thanh toán trực tuyến |
| **Jinja2** | 3.1.2 | Template engine render HTML |
| **Werkzeug** | 3.0.3 | Bảo mật (hash password), upload file |

---

## 📁 Cấu Trúc Thư Mục Chi Tiết

```
KhacQuanMotorbikeRental/
│
├── 📄 app.py                    # File khởi tạo tables trong database
├── 📄 runlocal.py               # File chạy server local (development)
├── 📄 wsgi.py                   # Entry point cho production (Gunicorn)
├── 📄 requirements.txt          # Danh sách thư viện Python cần cài
├── 📄 Procfile                  # Config cho Heroku deployment
├── 📄 .env                      # Biến môi trường (DB_URL, SECRET_KEY, VNPay config)
│
└── 📂 app/                      # Package chính của ứng dụng
    │
    ├── 📄 __init__.py           # Khởi tạo Flask app, đăng ký routes
    ├── 📄 models.py             # Định nghĩa các Model (tables) trong database
    ├── 📄 extensions.py         # Utility functions (kết nối DB session)
    ├── 📄 db_connect.py         # Test kết nối database
    ├── 📄 vnpay_helper.py       # Helper class xử lý VNPay API
    │
    ├── 📂 routes/               # Các module xử lý routing (URL endpoints)
    │   ├── 📄 __init__.py       # Đăng ký Blueprint chính
    │   ├── 📄 main.py           # Routes trang chủ, about, contact
    │   ├── 📄 auth.py           # Login/Logout/Register admin
    │   ├── 📄 motorcycle.py     # API quản lý xe máy (CRUD)
    │   ├── 📄 rental.py         # Đặt xe, xử lý thuê xe
    │   ├── 📄 vnpay.py          # Thanh toán VNPay
    │   ├── 📄 article.py        # Quản lý bài viết
    │   ├── 📄 info.py           # Thông tin cửa hàng
    │   └── 📄 admin_management.py # Dashboard admin, quản lý đơn hàng
    │
    ├── 📂 templates/            # File HTML (Jinja2 templates)
    │   ├── 📄 index.html        # Trang chủ khách hàng
    │   ├── 📄 payment_return.html # Trang callback sau thanh toán VNPay
    │   └── 📂 admin/            # Các trang admin dashboard
    │       ├── index.html
    │       ├── auth-sign-in.html
    │       ├── rentals.html
    │       └── ...
    │
    └── 📂 static/               # File tĩnh (CSS, JS, images)
        ├── 📂 css/              # Stylesheet files
        ├── 📂 js/               # JavaScript files
        ├── 📂 images/           # Hình ảnh
        └── 📂 uploads/          # File upload (CCCD, giấy phép lái xe)
            ├── citizen_id/      # Ảnh CCCD khách hàng
            └── motorcycles/     # Ảnh xe máy
```

---

## 🔄 Luồng Hoạt Động Hệ Thống

### 📖 Ví Dụ: Luồng Đặt Xe và Thanh Toán

Hãy theo dõi hành trình của khách hàng **Nguyễn Văn A** khi thuê xe SH 150i từ trang web:

#### **Bước 1: Khách hàng truy cập trang chủ**
```
USER → Browser: http://yourdomain.com/
↓
routes/main.py (@bp.route('/'))
↓
Render template: templates/index.html
↓
Hiển thị danh sách xe từ database (table: catagory_motorcycle)
```

**File liên quan:**
- `app/routes/main.py`: Xử lý route `/`
- `app/templates/index.html`: Giao diện trang chủ
- `app/models.py`: Model `Catagory_Motorcycle` chứa thông tin xe

**Chi tiết kỹ thuật:**
```python
# Trong routes/main.py
@bp.route('/')
def index():
    session = get_db_session()
    motorcycles = session.query(Catagory_Motorcycle).all()
    return render_template('index.html', motorcycles=motorcycles)
```

---

#### **Bước 2: Chọn xe và điền form đặt xe**
```
USER clicks "Đặt xe ngay" trên SH 150i
↓
Hiển thị modal/form với các trường:
  - Họ tên: Nguyễn Văn A
  - Số điện thoại: 0901234567
  - Email: vana@gmail.com
  - Ngày sinh: 15/03/1995
  - Quê quán: Hà Nội
  - Địa chỉ: 123 Láng Hạ
  - Số CCCD: 001095012345
  - Upload ảnh CCCD mặt trước
  - Upload ảnh CCCD mặt sau
  - Ngày bắt đầu thuê: 25/11/2025
  - Ngày kết thúc: 27/11/2025 (3 ngày)
  - Số lượng xe: 1
```

**File liên quan:**
- `app/templates/index.html`: HTML form với `<form>` và `<input>` fields
- `app/static/js/`: JavaScript xử lý submit form

---

#### **Bước 3: Submit form → Server xử lý**
```
USER clicks "Xác nhận đặt xe"
↓
POST /api/rental/submit (form data + files)
↓
routes/rental.py (@bp.route('/api/rental/submit'))
↓
Xử lý logic:
  1. Validate dữ liệu (kiểm tra required fields)
  2. Lưu ảnh CCCD vào static/uploads/citizen_id/
  3. Tạo/Update Customer trong database
  4. Tính toán:
     - SH 150i: 200,000 VNĐ/ngày
     - 3 ngày × 200,000 = 600,000 VNĐ
     - Cọc 50%: 300,000 VNĐ
  5. Tạo Rental record (status: 'pending')
  6. Tạo RentalItem (liên kết xe với đơn hàng)
  7. Tạo Payment record (status: 'pending')
  8. Generate order_id: 20251125143022_1234
  9. Gọi VNPay API tạo payment URL
↓
Return JSON: { "success": true, "payment_url": "https://sandbox.vnpayment.vn/..." }
```

**File liên quan:**
- `app/routes/rental.py`: Function `submit_rental()`
- `app/models.py`: Models `Customer`, `Rental`, `RentalItem`, `Payment`
- `app/vnpay_helper.py`: Class `VNPay` xử lý API
- `app/extensions.py`: Function `get_db_session()` tạo database session

**Chi tiết kỹ thuật:**
```python
# Trong routes/rental.py
@bp.route('/api/rental/submit', methods=['POST'])
def submit_rental():
    # 1. Lấy dữ liệu form
    full_name = request.form.get('full_name')  # "Nguyễn Văn A"
    citizen_id = request.form.get('citizen_id')  # "001095012345"
    
    # 2. Xử lý upload file
    front_image = save_uploaded_file(
        request.files['citizen_id_front_image'],
        folder='uploads/citizen_id'
    )
    # → Lưu vào: static/uploads/citizen_id/20251125_143000_cccd_front.jpg
    
    # 3. Tạo Customer
    customer = Customer(
        full_name=full_name,
        citizen_id=citizen_id,
        citizen_id_front_image=front_image,
        ...
    )
    session.add(customer)
    session.flush()  # Lấy customer.id
    
    # 4. Tính giá
    price_per_day = 200000  # SH 150i
    days = 3
    total_amount = price_per_day * days  # 600,000
    deposit_amount = total_amount * 0.5  # 300,000
    
    # 5. Tạo Rental
    rental = Rental(
        customer_id=customer.id,
        start_date=datetime(2025, 11, 25),
        end_date=datetime(2025, 11, 27),
        rental_days=3,
        total_amount=600000,
        deposit_amount=300000,
        status='pending',
        payment_status='pending'
    )
    session.add(rental)
    
    # 6. Gọi VNPay
    vnp = VNPay()
    payment_url = vnp.create_payment_request(
        order_id="20251125143022_1234",
        amount=300000,
        order_desc="Dat xe SH 150i - 1 xe - 3 ngay"
    )
    
    session.commit()
    return jsonify({'success': True, 'payment_url': payment_url})
```

---

#### **Bước 4: Redirect đến VNPay thanh toán**
```
Browser tự động redirect đến:
https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=30000000&vnp_TxnRef=20251125143022_1234&...
↓
USER chọn ngân hàng: NCB Bank
USER nhập thông tin thẻ và xác thực OTP
↓
VNPay xử lý thanh toán
```

**Thuật ngữ:**
- **vnp_Amount**: Số tiền (đơn vị: đồng × 100, ví dụ 300,000 VNĐ = 30,000,000)
- **vnp_TxnRef**: Mã đơn hàng (order_id) duy nhất
- **vnp_HashSecret**: Key bí mật để mã hóa/xác thực giao dịch

---

#### **Bước 5: VNPay callback về server**
```
Thanh toán thành công
↓
VNPay redirect về:
https://yourdomain.com/payment/return?vnp_ResponseCode=00&vnp_TxnRef=20251125143022_1234&vnp_TransactionNo=14231122&...
↓
routes/rental.py (@bp.route('/payment/return'))
↓
Xử lý:
  1. Validate chữ ký VNPay (security check)
  2. Tìm Payment record bằng order_id
  3. Kiểm tra vnp_ResponseCode:
     - "00" = Thành công
     - "07" = Nghi ngờ gian lận
     - "51" = Không đủ tiền
  4. Nếu thành công:
     - Update Payment: status = 'paid'
     - Update Rental: paid_amount = 300,000, status = 'confirmed'
  5. Commit database
↓
Render template: payment_return.html (Thông báo thành công)
```

**File liên quan:**
- `app/routes/rental.py`: Function `payment_return()`
- `app/vnpay_helper.py`: Method `validate_response()`
- `app/templates/payment_return.html`: Trang kết quả thanh toán

**Chi tiết kỹ thuật:**
```python
# Trong routes/rental.py
@bp.route('/payment/return', methods=['GET'])
def payment_return():
    # 1. Lấy callback data từ VNPay
    callback_data = {k: v for k, v in request.args.items() if k.startswith('vnp_')}
    # Ví dụ: {'vnp_ResponseCode': '00', 'vnp_TxnRef': '20251125143022_1234', ...}
    
    # 2. Validate chữ ký
    vnp = VNPay()
    vnp.responseData = callback_data
    if not vnp.validate_response():
        return render_template('payment_return.html', success=False, 
                             message='Sai chữ ký xác thực!')
    
    # 3. Kiểm tra kết quả
    response_code = callback_data.get('vnp_ResponseCode')
    if response_code == '00':  # Thành công
        # 4. Update database
        payment.payment_status = 'paid'
        rental.status = 'confirmed'
        rental.paid_amount = 300000
        session.commit()
        
        return render_template('payment_return.html', 
                             success=True, 
                             message='Thanh toán thành công!')
```

---

#### **Bước 6: Admin quản lý đơn hàng**
```
Admin login: http://yourdomain.com/admin/login
↓
routes/auth.py (@bp.route('/admin/login'))
↓
Dashboard: http://yourdomain.com/admin/
↓
routes/admin_management.py (@bp.route('/admin/rentals'))
↓
Hiển thị danh sách đơn hàng:
  - Đơn #20251125143022_1234
  - Khách: Nguyễn Văn A (0901234567)
  - Xe: SH 150i
  - Ngày: 25/11/2025 → 27/11/2025
  - Trạng thái: Confirmed (Đã cọc)
  - Còn nợ: 300,000 VNĐ
↓
Admin chọn xe cụ thể từ kho (ví dụ: SH 150i biển 29A-12345)
Admin giao xe cho khách
```

**File liên quan:**
- `app/routes/auth.py`: Login/Logout admin
- `app/routes/admin_management.py`: Dashboard, quản lý đơn hàng
- `app/templates/admin/rentals.html`: Giao diện danh sách đơn

---

#### **Bước 7: Trả xe và thanh toán phần còn lại**
```
Khách trả xe ngày 27/11/2025
↓
Admin kiểm tra xe (còn nguyên vẹn)
Admin cập nhật: actual_return_date = 27/11/2025
↓
Hệ thống tính:
  - Số ngày thực tế: 3 ngày (đúng hợp đồng)
  - Tổng tiền: 600,000 VNĐ
  - Đã trả: 300,000 VNĐ (cọc)
  - Còn lại: 300,000 VNĐ
↓
Khách thanh toán 300,000 VNĐ (tiền mặt hoặc VNPay)
↓
Admin xác nhận → Update:
  - Rental: status = 'returned', payment_status = 'paid'
  - Motorcycle: status = 'ready' (sẵn sàng cho thuê tiếp)
```

---

## 🗄️ Mô Hình Dữ Liệu

### Sơ đồ quan hệ các bảng (ERD)

```
┌─────────────────┐
│   Accounts      │  (Tài khoản admin)
├─────────────────┤
│ id (PK)         │
│ username        │
│ password_hash   │
│ full_name       │
│ email           │
│ role            │
└─────────────────┘

┌─────────────────────┐
│ Catagory_Motorcycle │  (Danh mục xe)
├─────────────────────┤
│ id (PK)             │
│ name                │  "Honda SH 150i"
│ brand               │  "Honda"
│ engine_capacity     │  "150cc"
│ price_per_day       │  200,000 VNĐ
│ price_per_week      │  1,200,000 VNĐ
│ price_per_month     │  4,500,000 VNĐ
│ image               │  "/uploads/sh150i.jpg"
└─────────────────────┘
         │
         │ 1:N (Một loại xe có nhiều xe cụ thể)
         ▼
┌─────────────────────┐
│    Motorcycles      │  (Chi tiết xe cụ thể)
├─────────────────────┤
│ id (PK)             │
│ category_id (FK)    │ → Catagory_Motorcycle.id
│ license_plate       │  "29A-12345" (biển số xe)
│ model_year          │  2023
│ status              │  "ready" / "rented" / "maintenance"
└─────────────────────┘

┌─────────────────┐
│    Customer     │  (Khách hàng)
├─────────────────┤
│ id (PK)         │
│ full_name       │  "Nguyễn Văn A"
│ phone           │  "0901234567"
│ email           │
│ date_of_birth   │  1995-03-15
│ hometown        │  "Hà Nội"
│ address         │  "123 Láng Hạ"
│ citizen_id      │  "001095012345" (UNIQUE)
│ citizen_id_front_image  │  "/uploads/citizen_id/..."
│ citizen_id_back_image   │
│ driver_license_number   │
└─────────────────┘
         │
         │ 1:N (Một khách có nhiều đơn hàng)
         ▼
┌─────────────────────┐
│      Rental         │  (Đơn thuê xe)
├─────────────────────┤
│ id (PK)             │
│ customer_id (FK)    │ → Customer.id
│ start_date          │  2025-11-25
│ end_date            │  2025-11-27
│ actual_return_date  │  (Ngày trả thực tế, NULL khi chưa trả)
│ rental_days         │  3
│ quantity            │  1
│ total_amount        │  600,000
│ deposit_amount      │  300,000
│ paid_amount         │  300,000 (đã trả)
│ status              │  "pending" / "confirmed" / "rented" / "returned" / "cancelled"
│ payment_status      │  "pending" / "partial" / "paid"
│ payment_method      │  "vnpay" / "cash"
│ vnpay_transaction_id│  "20251125143022_1234"
│ notes               │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│    RentalItem       │  (Chi tiết xe trong đơn)
├─────────────────────┤
│ id (PK)             │
│ rental_id (FK)      │ → Rental.id
│ motorcycle_id (FK)  │ → Motorcycles.id (Xe cụ thể được giao)
│ price_per_day       │  200,000
└─────────────────────┘

         ┌─────────────────────┐
         │      Payment        │  (Lịch sử thanh toán)
         ├─────────────────────┤
         │ id (PK)             │
         │ rental_id (FK)      │ → Rental.id
         │ payment_code        │  "20251125143022_1234"
         │ amount              │  300,000
         │ payment_method      │  "vnpay"
         │ payment_status      │  "paid"
         │ vnpay_transaction_id│  "14231122" (Mã GD từ VNPay)
         │ vnpay_bank_code     │  "NCB"
         │ vnpay_pay_date      │  2025-11-25 14:35:00
         │ payment_date        │  2025-11-25 14:35:00
         └─────────────────────┘

┌─────────────────┐
│   StoreInfo     │  (Thông tin cửa hàng)
├─────────────────┤
│ id (PK)         │
│ store_name      │  "Khắc Quân Motorbike"
│ owner_name      │
│ address         │
│ phone           │  "0912345678"
│ email           │
│ business_hours  │  "8:00 - 22:00"
│ google_map_url  │
│ description     │
└─────────────────┘

┌─────────────────┐
│    Article      │  (Bài viết/Tin tức)
├─────────────────┤
│ id (PK)         │
│ title           │  "Top 10 địa điểm du lịch..."
│ content         │  (HTML content)
│ featured_image  │
│ is_published    │  true/false
│ view_count      │  150
│ published_at    │  2025-11-20
└─────────────────┘
```

### Giải thích quan hệ:
- **(FK)**: Foreign Key - Khóa ngoại liên kết với bảng khác
- **(PK)**: Primary Key - Khóa chính duy nhất
- **1:N**: Quan hệ một-nhiều (ví dụ: 1 Customer có N Rentals)

---

## 🚀 Hướng Dẫn Cài Đặt

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/KhacQuanMotorbikeRental.git
cd KhacQuanMotorbikeRental
```

### 2. Tạo Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 4. Cấu hình file `.env`
Tạo file `.env` trong thư mục gốc:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/motorbike_rental

# Flask
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development

# VNPay (Sandbox)
VNPAY_TMN_CODE=YOUR_TMN_CODE
VNPAY_HASH_SECRET=YOUR_HASH_SECRET
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:5000/payment/return
```

### 5. Khởi tạo Database
```bash
python app.py
# Output: "Bảng đã được tạo (nếu chưa tồn tại)."
```

### 6. Chạy Server
```bash
# Development
python runlocal.py

# Production (Gunicorn)
gunicorn wsgi:app
```

### 7. Truy cập ứng dụng
- **Trang chủ**: http://localhost:5000/
- **Admin login**: http://localhost:5000/admin/login

---

## 📚 Các Thuật Ngữ Quan Trọng

### 1. Flask Framework
**Định nghĩa**: Framework web nhẹ của Python, giúp xây dựng web app nhanh chóng.

**Thành phần chính:**
- **Route**: Mapping giữa URL và function xử lý
  ```python
  @bp.route('/hello')
  def hello():
      return "Hello World"
  ```
- **Blueprint**: Module con để tổ chức code, dễ quản lý
  ```python
  bp = Blueprint('main', __name__)
  ```
- **Template**: File HTML động sử dụng Jinja2
  ```html
  <h1>Welcome {{ user.name }}</h1>
  ```

---

### 2. ORM (Object-Relational Mapping)
**Định nghĩa**: Công nghệ ánh xạ giữa Object (Python class) và Table (Database).

**Ví dụ với SQLAlchemy:**
```python
# Thay vì viết SQL:
# SELECT * FROM customer WHERE phone = '0901234567'

# Dùng ORM:
customer = session.query(Customer).filter(Customer.phone == '0901234567').first()
```

**Lợi ích:**
- Không cần viết SQL thuần
- Bảo mật chống SQL Injection tự động
- Code dễ đọc, dễ bảo trì

---

### 3. Database Session
**Định nghĩa**: Phiên làm việc với database, quản lý các thao tác CRUD (Create, Read, Update, Delete).

**Vòng đời Session:**
```python
session = get_db_session()  # 1. Mở session
try:
    customer = Customer(...)
    session.add(customer)   # 2. Thêm object vào session
    session.commit()        # 3. Lưu vào database
except:
    session.rollback()      # 4. Rollback nếu lỗi
finally:
    session.close()         # 5. Đóng session
```

**Thuật ngữ:**
- **Flush**: Đẩy data tạm vào DB để lấy ID (chưa commit)
- **Commit**: Lưu thay đổi vĩnh viễn vào database
- **Rollback**: Hủy bỏ tất cả thay đổi trong session

---

### 4. VNPay Payment Gateway
**Định nghĩa**: Cổng thanh toán trực tuyến của Việt Nam, hỗ trợ thanh toán qua thẻ ATM, thẻ tín dụng.

**Quy trình tích hợp:**
```
1. Merchant (Website) tạo payment request
   ↓ (gửi params: amount, order_id, vnp_SecureHash)
2. VNPay hiển thị trang thanh toán
   ↓ (User nhập thông tin thẻ)
3. VNPay xử lý thanh toán
   ↓ (callback về return_url)
4. Merchant validate response (kiểm tra chữ ký)
   ↓ (update database)
5. Hiển thị kết quả cho User
```

**Tham số quan trọng:**
- `vnp_Amount`: Số tiền (× 100)
- `vnp_TxnRef`: Mã đơn hàng duy nhất
- `vnp_SecureHash`: Chữ ký SHA256 để bảo mật
- `vnp_ResponseCode`: Mã kết quả ("00" = thành công)

---

### 5. WSGI (Web Server Gateway Interface)
**Định nghĩa**: Giao thức chuẩn giữa web server (Nginx, Apache) và Python application.

**Kiến trúc Production:**
```
Internet → Nginx (Reverse Proxy)
           ↓
        Gunicorn (WSGI Server)
           ↓
        Flask App (Python)
           ↓
        PostgreSQL Database
```

**File wsgi.py:**
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

---

### 6. File Upload Security
**Vấn đề bảo mật:**
- User có thể upload file độc hại (.exe, .php)
- Tên file có thể chứa ký tự đặc biệt: `../../../etc/passwd`

**Giải pháp:**
```python
from werkzeug.utils import secure_filename

# Trước khi lưu file:
filename = secure_filename(file.filename)
# Input: "../../../malicious.exe"
# Output: "malicious.exe"

# Kiểm tra extension:
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
if not allowed_file(filename):
    return error("File không hợp lệ")
```

---

### 7. Environment Variables (.env)
**Định nghĩa**: Biến môi trường lưu thông tin nhạy cảm (password, API key) riêng biệt khỏi source code.

**Tại sao quan trọng:**
- Không commit secret keys lên Git
- Dễ dàng thay đổi config giữa dev/production
- Bảo mật thông tin nhạy cảm

**Cách sử dụng:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Đọc file .env

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
DB_URL = os.getenv('DATABASE_URL')
```

---

### 8. Jinja2 Template Engine
**Định nghĩa**: Công cụ render HTML động trong Flask.

**Syntax cơ bản:**
```html
<!-- Biến -->
<h1>Welcome {{ user.name }}</h1>

<!-- Vòng lặp -->
{% for motorcycle in motorcycles %}
  <div class="card">{{ motorcycle.name }}</div>
{% endfor %}

<!-- Điều kiện -->
{% if user.is_authenticated %}
  <a href="/logout">Logout</a>
{% else %}
  <a href="/login">Login</a>
{% endif %}

<!-- Include template khác -->
{% include 'partials/header.html' %}
```

---

### 9. Status & State Management
**Các trạng thái quan trọng:**

**Rental Status:**
- `pending`: Chờ thanh toán cọc
- `confirmed`: Đã cọc, chờ nhận xe
- `rented`: Đang thuê (đã giao xe)
- `returned`: Đã trả xe
- `cancelled`: Đã hủy

**Payment Status:**
- `pending`: Chờ thanh toán
- `partial`: Đã thanh toán một phần (cọc)
- `paid`: Đã thanh toán đầy đủ
- `failed`: Thanh toán thất bại

**Motorcycle Status:**
- `ready`: Sẵn sàng cho thuê
- `rented`: Đang được thuê
- `maintenance`: Đang bảo trì
- `unavailable`: Không khả dụng

---

### 10. RESTful API Principles
**Định nghĩa**: Phong cách thiết kế API sử dụng HTTP methods đúng cách.

**HTTP Methods:**
```python
# GET: Lấy dữ liệu (không thay đổi database)
@bp.route('/api/motorcycles', methods=['GET'])
def get_motorcycles():
    return jsonify(motorcycles)

# POST: Tạo mới
@bp.route('/api/motorcycles', methods=['POST'])
def create_motorcycle():
    ...

# PUT/PATCH: Cập nhật
@bp.route('/api/motorcycles/<id>', methods=['PUT'])
def update_motorcycle(id):
    ...

# DELETE: Xóa
@bp.route('/api/motorcycles/<id>', methods=['DELETE'])
def delete_motorcycle(id):
    ...
```

**Response format:**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful"
}
```

---

## 🔐 Bảo Mật

### Các biện pháp bảo mật đã triển khai:

1. **Password Hashing**: Sử dụng `werkzeug.security.generate_password_hash`
   ```python
   # KHÔNG bao giờ lưu plain password
   password_hash = generate_password_hash("user_password")
   ```

2. **CSRF Protection**: Flask session cookie với `secret_key`

3. **SQL Injection Prevention**: SQLAlchemy ORM tự động escape

4. **File Upload Validation**: Kiểm tra extension và secure filename

5. **VNPay Signature Validation**: Xác thực chữ ký SHA256

6. **Session Management**: Auto expire và secure cookies

---

## 📝 Ghi Chú Quan Trọng

### ⚠️ TODO/Improvements:
- [ ] Thêm authentication middleware cho admin routes
- [ ] Implement Redis cache cho danh sách xe
- [ ] Thêm email notification (xác nhận đơn hàng, nhắc trả xe)
- [ ] Tích hợp SMS OTP khi đặt xe
- [ ] Thêm rating/review system
- [ ] Export báo cáo doanh thu Excel/PDF
- [ ] Thêm real-time notification (WebSocket)

### 📞 Liên Hệ
- **Developer**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: https://github.com/cnv1902/KhacQuanMotorbikeRental

---

## 📄 License
MIT License - Tự do sử dụng và chỉnh sửa cho mục đích học tập và thương mại.

---

**🎓 Tài Liệu Tham Khảo:**
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [VNPay Integration Guide](https://sandbox.vnpayment.vn/apis/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

*README này được tạo với ❤️ để giúp developers hiểu rõ hệ thống*
