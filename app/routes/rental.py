from flask import jsonify, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from decimal import Decimal
import os
import random
from . import bp
from app.extensions import get_db_session
from app.models import Customer, Rental, RentalItem, Payment, Catagory_Motorcycle
from app.vnpay_helper import VNPay, get_client_ip


def generate_order_id():
    """Generate unique order ID"""
    return datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, folder='uploads/citizen_id'):
    """Save uploaded file and return relative path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        # Create upload directory if not exists (relative to app/static)
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', folder)
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Return relative path for database (from static folder)
        return os.path.join(folder, filename)
    return None


@bp.route('/rental/health')
def rental_health():
    return jsonify({'ok': True, 'service': 'rental'})


@bp.route('/api/rental/submit', methods=['POST'])
def submit_rental():
    """Xử lý submit form đặt xe"""
    try:
        session = get_db_session()
        
        try:
            # Get form data
            motorcycle_id = request.form.get('motorcycle_id')
            quantity = int(request.form.get('quantity', 1))
            days = int(request.form.get('days', 1))
            
            # Rental dates
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            
            # Parse rental dates
            start_date = None
            end_date = None
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Validate dates
            if start_date and end_date:
                if end_date < start_date:
                    return jsonify({'success': False, 'message': 'Ngày kết thúc phải sau ngày bắt đầu!'}), 400
                # Recalculate days from dates
                days = (end_date - start_date).days + 1
                if days < 1:
                    return jsonify({'success': False, 'message': 'Số ngày thuê không hợp lệ!'}), 400
            
            # Customer information
            full_name = request.form.get('full_name')
            phone = request.form.get('phone')
            email = request.form.get('email') or None
            date_of_birth_str = request.form.get('date_of_birth')
            hometown = request.form.get('hometown')
            address = request.form.get('address')
            citizen_id = request.form.get('citizen_id')
            
            # Parse date of birth
            date_of_birth = None
            if date_of_birth_str:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
            
            # Validate required fields
            if not all([motorcycle_id, full_name, phone, date_of_birth, hometown, address, citizen_id, start_date, end_date]):
                return jsonify({'success': False, 'message': 'Vui lòng điền đầy đủ thông tin bắt buộc!'}), 400
            
            # Check if customer exists by citizen_id
            customer = session.query(Customer).filter(Customer.citizen_id == citizen_id).first()
            
            # Save uploaded images
            front_image = None
            back_image = None
            
            if 'citizen_id_front_image' in request.files:
                file = request.files['citizen_id_front_image']
                if file.filename:
                    front_image = save_uploaded_file(file, 'uploads/citizen_id')
            
            if 'citizen_id_back_image' in request.files:
                file = request.files['citizen_id_back_image']
                if file.filename:
                    back_image = save_uploaded_file(file, 'uploads/citizen_id')
            
            if not front_image or not back_image:
                return jsonify({'success': False, 'message': 'Vui lòng upload đầy đủ ảnh CCCD!'}), 400
            
            # Create or update customer
            if customer:
                # Update existing customer
                customer.full_name = full_name
                customer.phone = phone
                customer.email = email
                customer.date_of_birth = date_of_birth
                customer.hometown = hometown
                customer.address = address
                customer.citizen_id_front_image = front_image
                customer.citizen_id_back_image = back_image
            else:
                # Create new customer
                customer = Customer(
                    full_name=full_name,
                    phone=phone,
                    email=email,
                    date_of_birth=date_of_birth,
                    hometown=hometown,
                    address=address,
                    citizen_id=citizen_id,
                    citizen_id_front_image=front_image,
                    citizen_id_back_image=back_image
                )
                session.add(customer)
            
            session.flush()  # Get customer ID
            
            # Get motorcycle category for price (motorcycle_id is actually category_id from form)
            motorcycle = session.query(Catagory_Motorcycle).filter(Catagory_Motorcycle.id == motorcycle_id).first()
            if not motorcycle:
                return jsonify({'success': False, 'message': 'Không tìm thấy xe máy!'}), 404
            
            price_per_day = float(motorcycle.price_per_day) if motorcycle.price_per_day else 0
            total_amount = price_per_day * quantity * days
            deposit_amount = total_amount * 0.5  # 50% deposit
            
            # Create rental order (pending payment)
            rental = Rental(
                customer_id=customer.id,
                start_date=start_date,
                end_date=end_date,
                rental_days=days,
                quantity=quantity,
                total_amount=Decimal(str(total_amount)),
                deposit_amount=Decimal(str(deposit_amount)),
                paid_amount=Decimal('0'),
                status='pending',
                payment_status='pending'
            )
            session.add(rental)
            session.flush()  # Get rental ID
            
            # Create rental items
            # Note: motorcycle_id in RentalItem refers to motorcycles table (Detail_Motorcycle)
            # For now, we'll use category_id as reference, but ideally should select available motorcycles
            # TODO: Implement logic to select available motorcycles from the category
            rental_item = RentalItem(
                rental_id=rental.id,
                motorcycle_id=None,  # Will be assigned when actual motorcycle is selected
                price_per_day=Decimal(str(price_per_day))
            )
            session.add(rental_item)
            
            # Generate order ID for VNPay
            order_id = generate_order_id()
            
            # Get client IP
            ip_addr = get_client_ip(request)
            order_desc = f"Dat xe {motorcycle.name if hasattr(motorcycle, 'name') else 'Xe may'} - {quantity} xe - {days} ngay"
            
            # Get return URL
            return_url = os.getenv('VNPAY_RETURN_URL', f"http://{request.host}/payment/return")
            
            # Create VNPay payment request
            vnp = VNPay()
            payment_url = vnp.create_payment_request(
                order_id=order_id,
                amount=deposit_amount,
                order_desc=order_desc,
                ip_addr=ip_addr,
                bank_code='',  # Empty to let VNPay choose
                return_url=return_url
            )
            
            # Store order_id in rental for reference
            rental.vnpay_transaction_id = order_id
            
            # Create payment record
            payment = Payment(
                rental_id=rental.id,
                payment_code=order_id,
                amount=Decimal(str(deposit_amount)),
                payment_method='vnpay',
                payment_status='pending'
            )
            session.add(payment)
            
            session.commit()
            
            return jsonify({
                'success': True,
                'payment_url': payment_url,
                'order_id': order_id,
                'message': 'Tạo yêu cầu thanh toán thành công!'
            })
            
        except Exception as e:
            session.rollback()
            return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'}), 500


@bp.route('/payment/return', methods=['GET'])
def payment_return():
    """Xử lý callback từ VNPay sau khi thanh toán"""
    try:
        session = get_db_session()
        
        try:
            # Get callback data from request (only vnp_* keys)
            callback_data = {k: v for k, v in request.args.items() if k.startswith('vnp_')}
            
            if not callback_data:
                return render_template('payment_return.html',
                                     success=False,
                                     message='Không có dữ liệu callback từ VNPay!')
            
            # Validate callback
            vnp = VNPay()
            vnp.responseData = callback_data
            
            # Debug: Print callback data
            print(f"VNPay Callback Data: {callback_data}")
            
            if not vnp.validate_response():
                return render_template('payment_return.html', 
                                     success=False,
                                     message='Sai chữ ký xác thực! Vui lòng kiểm tra lại cấu hình VNPAY_HASH_SECRET trong file .env')
            
            # Get response data
            order_id = callback_data.get('vnp_TxnRef', '')
            response_code = callback_data.get('vnp_ResponseCode', '')
            transaction_status = callback_data.get('vnp_TransactionStatus', '')
            transaction_no = callback_data.get('vnp_TransactionNo', '')
            amount = float(callback_data.get('vnp_Amount', 0)) / 100  # Convert from cents
            bank_code = callback_data.get('vnp_BankCode', '')
            pay_date = callback_data.get('vnp_PayDate', '')
            
            # Determine payment success
            payment_success = False
            if response_code:
                payment_success = (response_code == '00')
            elif transaction_status:
                payment_success = (transaction_status == '00')
            else:
                payment_success = (transaction_no and transaction_no != '0')
            
            # Find payment by order_id (payment_code)
            payment = session.query(Payment).filter(Payment.payment_code == order_id).first()
            
            if not payment:
                # Try to find by rental's vnpay_transaction_id (for backward compatibility)
                rental = session.query(Rental).filter(Rental.vnpay_transaction_id == order_id).first()
                if rental:
                    payment = session.query(Payment).filter(Payment.rental_id == rental.id).order_by(Payment.id.desc()).first()
            
            if not payment:
                return render_template('payment_return.html',
                                     success=False,
                                     message='Không tìm thấy giao dịch thanh toán!')
            
            rental = session.query(Rental).filter(Rental.id == payment.rental_id).first()
            if not rental:
                return render_template('payment_return.html',
                                     success=False,
                                     message='Không tìm thấy đơn hàng!')
            
            if payment_success:  # Payment success
                # Update payment record
                payment.payment_status = 'paid'
                payment.vnpay_transaction_id = transaction_no
                payment.vnpay_bank_code = bank_code
                if pay_date:
                    try:
                        payment.vnpay_pay_date = datetime.strptime(pay_date, '%Y%m%d%H%M%S')
                    except:
                        pass
                payment.payment_date = datetime.now()
                
                # Update rental - add to paid amount
                current_paid = rental.paid_amount or Decimal('0')
                rental.paid_amount = current_paid + Decimal(str(amount))
                rental.vnpay_bank_code = bank_code
                rental.payment_method = 'vnpay'
                
                # If rental has actual_return_date, it means it's a return payment
                # Calculate total amount and check if fully paid
                if rental.actual_return_date:
                    # Get all rental items with assigned motorcycles
                    from app.models import RentalItem, Motorcycles
                    items = session.query(RentalItem).filter(
                        RentalItem.rental_id == rental.id,
                        RentalItem.motorcycle_id.isnot(None)
                    ).all()
                    
                    # Calculate total amount based on actual days
                    if items and rental.start_date:
                        time_diff = rental.actual_return_date - rental.start_date
                        actual_days = max(1, (time_diff.days + 1))
                        total_amount = Decimal('0')
                        for item in items:
                            if item.price_per_day:
                                total_amount += Decimal(str(item.price_per_day)) * actual_days
                        rental.total_amount = total_amount
                        
                        # Check if fully paid
                        if rental.paid_amount >= total_amount:
                            rental.payment_status = 'paid'
                            rental.status = 'returned'
                            
                            # Update all motorcycles status to 'ready'
                            for item in items:
                                if item.motorcycle_id:
                                    motorcycle = session.query(Motorcycles).filter(Motorcycles.id == item.motorcycle_id).first()
                                    if motorcycle:
                                        motorcycle.status = 'ready'
                        else:
                            rental.payment_status = 'partial'
                    else:
                        rental.payment_status = 'paid'
                        rental.status = 'returned'
                else:
                    # Initial deposit payment
                    rental.status = 'confirmed'
                    rental.payment_status = 'paid'
                
                session.commit()
                
                # Check if payment is from admin (via query parameter)
                is_admin = request.args.get('admin') == '1'
                rental_id_param = request.args.get('rental_id')
                
                if is_admin and rental_id_param:
                    # Redirect to admin rentals page
                    return redirect(url_for('admin.rentals'))
                
                # Get customer info for display
                customer = session.query(Customer).filter(Customer.id == rental.customer_id).first()
                
                return render_template('payment_return.html',
                                     success=True,
                                     message='Thanh toán thành công!',
                                     rental=rental,
                                     customer=customer,
                                     transaction_no=transaction_no,
                                     amount=amount)
            else:
                # Payment failed or pending
                # TransactionStatus '02' might mean pending, so we keep it as pending
                if transaction_status == '02':
                    rental.status = 'pending'
                    rental.payment_status = 'pending'
                else:
                    rental.status = 'cancelled'
                    rental.payment_status = 'failed'
                
                session.commit()
                
                # Determine error message
                error_msg = 'Thanh toán thất bại!'
                if transaction_status == '02':
                    # Check if it's a "bank not supported" case
                    if bank_code == 'VNPAY' and transaction_no == '0':
                        error_msg = 'Ngân hàng thanh toán không được hỗ trợ. Vui lòng thử lại với phương thức thanh toán khác.'
                    else:
                        error_msg = 'Giao dịch đang được xử lý. Vui lòng chờ xác nhận từ VNPay.'
                elif response_code:
                    # Map common error codes
                    error_codes = {
                        '07': 'Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).',
                        '09': 'Thẻ/Tài khoản chưa đăng ký dịch vụ InternetBanking',
                        '10': 'Xác thực thông tin thẻ/tài khoản không đúng quá 3 lần',
                        '11': 'Đã hết hạn chờ thanh toán. Xin vui lòng thực hiện lại giao dịch.',
                        '12': 'Thẻ/Tài khoản bị khóa.',
                        '13': 'Nhập sai mật khẩu xác thực giao dịch (OTP). Xin vui lòng thực hiện lại giao dịch.',
                        '51': 'Tài khoản không đủ số dư để thực hiện giao dịch.',
                        '65': 'Tài khoản đã vượt quá hạn mức giao dịch trong ngày.',
                        '75': 'Ngân hàng thanh toán đang bảo trì.',
                        '79': 'Nhập sai mật khẩu thanh toán quá số lần quy định.'
                    }
                    if response_code in error_codes:
                        error_msg = f'Thanh toán thất bại! {error_codes[response_code]}'
                    else:
                        error_msg = f'Thanh toán thất bại! Mã lỗi: {response_code}'
                elif transaction_status:
                    error_msg = f'Thanh toán thất bại! Trạng thái: {transaction_status}'
                
                return render_template('payment_return.html',
                                     success=False,
                                     message=error_msg,
                                     response_code=response_code or transaction_status)
            
        except Exception as e:
            session.rollback()
            return render_template('payment_return.html',
                                 success=False,
                                 message=f'Lỗi xử lý: {str(e)}')
        finally:
            session.close()
            
    except Exception as e:
        return render_template('payment_return.html',
                             success=False,
                             message=f'Lỗi hệ thống: {str(e)}')
