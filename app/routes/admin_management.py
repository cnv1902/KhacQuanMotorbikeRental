"""
Admin routes for managing customers, rentals, and payments
"""
from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import desc, func
from datetime import datetime
from decimal import Decimal
import os
import random
from . import bp
from app.extensions import get_db_session
from app.models import Customer, Rental, RentalItem, Payment, Catagory_Motorcycle, Motorcycles
from app.vnpay_helper import VNPay, get_client_ip


# ==================== CUSTOMER MANAGEMENT ====================

@bp.route('/admin/customers')
def customers():
    """Quản lý khách hàng"""
    session = get_db_session()
    try:
        # Get search and filter parameters
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = 20
        
        query = session.query(Customer)
        
        # Apply search filter
        if search:
            query = query.filter(
                (Customer.full_name.ilike(f'%{search}%')) |
                (Customer.phone.ilike(f'%{search}%')) |
                (Customer.email.ilike(f'%{search}%')) |
                (Customer.citizen_id.ilike(f'%{search}%'))
            )
        
        # Order by created_at desc
        query = query.order_by(desc(Customer.created_at))
        
        # Pagination
        total = query.count()
        customers_list = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get rental counts for each customer
        for customer in customers_list:
            customer.rental_count = session.query(Rental).filter(Rental.customer_id == customer.id).count()
        
        return render_template('admin/customers.html',
                             customers=customers_list,
                             search=search,
                             page=page,
                             per_page=per_page,
                             total=total,
                             total_pages=(total + per_page - 1) // per_page)
    finally:
        session.close()


@bp.route('/admin/customer/<int:customer_id>')
def customer_detail(customer_id):
    """Chi tiết khách hàng"""
    session = get_db_session()
    try:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            flash('Không tìm thấy khách hàng!', 'error')
            return redirect(url_for('admin.customers'))
        
        # Get rentals of this customer
        rentals = session.query(Rental).filter(Rental.customer_id == customer_id).order_by(desc(Rental.created_at)).all()
        
        return render_template('admin/customer_detail.html',
                             customer=customer,
                             rentals=rentals)
    finally:
        session.close()


# ==================== RENTAL MANAGEMENT ====================

@bp.route('/admin/rentals')
def rentals():
    """Quản lý đơn thuê"""
    session = get_db_session()
    try:
        # Get filter parameters
        status = request.args.get('status', '').strip()
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = 20
        
        query = session.query(Rental).outerjoin(Customer)
        
        # Apply status filter
        if status:
            query = query.filter(Rental.status == status)
        
        # Apply search filter
        if search:
            try:
                # Try to convert search to int for ID search
                search_int = int(search)
                query = query.filter(
                    (Rental.id == search_int) |
                    (Rental.vnpay_transaction_id.ilike(f'%{search}%')) |
                    (Customer.full_name.ilike(f'%{search}%')) |
                    (Customer.phone.ilike(f'%{search}%'))
                )
            except ValueError:
                # If not a number, search in text fields
                query = query.filter(
                    (Rental.vnpay_transaction_id.ilike(f'%{search}%')) |
                    (Customer.full_name.ilike(f'%{search}%')) |
                    (Customer.phone.ilike(f'%{search}%'))
                )
        
        # Order by created_at desc
        query = query.order_by(desc(Rental.created_at))
        
        # Pagination
        total = query.count()
        rentals_list = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return render_template('admin/rentals.html',
                             rentals=rentals_list,
                             status=status,
                             search=search,
                             page=page,
                             per_page=per_page,
                             total=total,
                             total_pages=(total + per_page - 1) // per_page)
    finally:
        session.close()


@bp.route('/admin/rental/<int:rental_id>')
def rental_detail(rental_id):
    """Chi tiết đơn thuê"""
    session = get_db_session()
    try:
        rental = session.query(Rental).filter(Rental.id == rental_id).first()
        if not rental:
            flash('Không tìm thấy đơn thuê!', 'error')
            return redirect(url_for('admin.rentals'))
        
        # Get customer
        customer = session.query(Customer).filter(Customer.id == rental.customer_id).first() if rental.customer_id else None
        
        # Get rental items
        items = session.query(RentalItem).filter(RentalItem.rental_id == rental_id).all()
        
        # Get payments
        payments = session.query(Payment).filter(Payment.rental_id == rental_id).order_by(desc(Payment.id)).all()
        
        # Get available motorcycles from rental items' categories
        # Find category IDs from rental items
        category_ids = set()
        for item in items:
            if item.motorcycle_id:
                motorcycle = session.query(Motorcycles).filter(Motorcycles.id == item.motorcycle_id).first()
                if motorcycle and motorcycle.category_id:
                    category_ids.add(motorcycle.category_id)
            # If no motorcycle assigned, try to find category by price_per_day
            elif item.price_per_day:
                # Find category with matching price_per_day
                category = session.query(Catagory_Motorcycle).filter(
                    Catagory_Motorcycle.price_per_day == item.price_per_day
                ).first()
                if category:
                    category_ids.add(category.id)
        
        # Get all motorcycles from these categories
        available_motorcycles = []
        if category_ids:
            available_motorcycles = session.query(Motorcycles).filter(
                Motorcycles.category_id.in_(list(category_ids))
            ).all()
        else:
            # If no category found, get all motorcycles
            available_motorcycles = session.query(Motorcycles).all()
        
        # Count assigned motorcycles
        assigned_motorcycles_count = len([item for item in items if item.motorcycle_id])
        
        return render_template('admin/rental_detail.html',
                             rental=rental,
                             customer=customer,
                             items=items,
                             payments=payments,
                             available_motorcycles=available_motorcycles,
                             assigned_motorcycles_count=assigned_motorcycles_count)
    finally:
        session.close()


@bp.route('/admin/rental/<int:rental_id>/update_status', methods=['POST'])
def rental_update_status(rental_id):
    """Cập nhật trạng thái đơn thuê"""
    session = get_db_session()
    try:
        rental = session.query(Rental).filter(Rental.id == rental_id).first()
        if not rental:
            return jsonify({'success': False, 'message': 'Không tìm thấy đơn thuê!'}), 404
        
        new_status = request.json.get('status')
        if new_status not in ['pending', 'confirmed', 'rented', 'returned', 'cancelled']:
            return jsonify({'success': False, 'message': 'Trạng thái không hợp lệ!'}), 400
        
        rental.status = new_status
        session.commit()
        
        return jsonify({'success': True, 'message': 'Cập nhật trạng thái thành công!'})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    finally:
        session.close()


@bp.route('/admin/rental/<int:rental_id>/assign_motorcycles', methods=['POST'])
def rental_assign_motorcycles(rental_id):
    """Gán xe cho đơn thuê - hỗ trợ gán nhiều xe"""
    session = get_db_session()
    try:
        rental = session.query(Rental).filter(Rental.id == rental_id).first()
        if not rental:
            return jsonify({'success': False, 'message': 'Không tìm thấy đơn thuê!'}), 404
        
        data = request.get_json()
        # New format: [{rental_item_id: 1, motorcycle_ids: [5, 6, 7]}, ...]
        assignments = data.get('assignments', [])
        
        if not assignments:
            return jsonify({'success': False, 'message': 'Không có xe nào được chọn!'}), 400
        
        updated_count = 0
        created_count = 0
        
        for assignment in assignments:
            rental_item_id = assignment.get('rental_item_id')  # Can be None
            motorcycle_ids = assignment.get('motorcycle_ids', [])
            
            # If motorcycle_ids is empty and rental_item_id exists, remove motorcycle from this item
            if (not motorcycle_ids or len(motorcycle_ids) == 0) and rental_item_id:
                original_item = session.query(RentalItem).filter(
                    RentalItem.id == rental_item_id,
                    RentalItem.rental_id == rental_id
                ).first()
                
                if original_item and original_item.motorcycle_id:
                    # Update motorcycle status back to ready if rental is not active
                    motorcycle = session.query(Motorcycles).filter(Motorcycles.id == original_item.motorcycle_id).first()
                    if motorcycle and rental.status not in ['confirmed', 'rented']:
                        motorcycle.status = 'ready'
                    
                    original_item.motorcycle_id = None
                    updated_count += 1
                continue
            
            if not motorcycle_ids or len(motorcycle_ids) == 0:
                continue
            
            # Get price_per_day from first motorcycle's category or from existing item
            first_motorcycle = session.query(Motorcycles).filter(Motorcycles.id == motorcycle_ids[0]).first()
            if not first_motorcycle:
                continue
            
            price_per_day = None
            if first_motorcycle.category_id:
                category = session.query(Catagory_Motorcycle).filter(Catagory_Motorcycle.id == first_motorcycle.category_id).first()
                if category:
                    price_per_day = category.price_per_day
            
            if not price_per_day:
                # Try to get from existing item if rental_item_id exists
                if rental_item_id:
                    original_item = session.query(RentalItem).filter(
                        RentalItem.id == rental_item_id,
                        RentalItem.rental_id == rental_id
                    ).first()
                    if original_item and original_item.price_per_day:
                        price_per_day = original_item.price_per_day
            
            if not price_per_day:
                continue  # Skip if no price found
            
            # Get or create rental items for each motorcycle
            for idx, motorcycle_id in enumerate(motorcycle_ids):
                motorcycle = session.query(Motorcycles).filter(Motorcycles.id == motorcycle_id).first()
                if not motorcycle:
                    continue
                
                # Check if this motorcycle is already assigned to a rental item
                existing_item = session.query(RentalItem).filter(
                    RentalItem.rental_id == rental_id,
                    RentalItem.motorcycle_id == motorcycle_id
                ).first()
                
                if existing_item:
                    # Already assigned, skip
                    continue
                
                if rental_item_id and idx == 0:
                    # Try to use existing item if provided
                    original_item = session.query(RentalItem).filter(
                        RentalItem.id == rental_item_id,
                        RentalItem.rental_id == rental_id
                    ).first()
                    
                    if original_item:
                        # Update existing item
                        original_item.motorcycle_id = motorcycle_id
                        original_item.price_per_day = price_per_day
                        # Update motorcycle status
                        if rental.status in ['confirmed', 'rented']:
                            motorcycle.status = 'rented'
                        updated_count += 1
                        continue
                
                # Create new rental item
                new_item = RentalItem(
                    rental_id=rental_id,
                    motorcycle_id=motorcycle_id,
                    price_per_day=price_per_day
                )
                session.add(new_item)
                # Update motorcycle status
                if rental.status in ['confirmed', 'rented']:
                    motorcycle.status = 'rented'
                created_count += 1
        
        session.commit()
        
        total = updated_count + created_count
        message = f'Đã gán {total} xe cho đơn thuê!'
        if created_count > 0:
            message += f' (Tạo mới {created_count} item)'
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    finally:
        session.close()


@bp.route('/admin/rental/<int:rental_id>/get_available_motorcycles', methods=['GET'])
def get_available_motorcycles(rental_id):
    """Lấy danh sách xe có thể gán cho đơn thuê"""
    session = get_db_session()
    try:
        rental = session.query(Rental).filter(Rental.id == rental_id).first()
        if not rental:
            return jsonify({'success': False, 'message': 'Không tìm thấy đơn thuê!'}), 404
        
        # Get rental items to find categories
        items = session.query(RentalItem).filter(RentalItem.rental_id == rental_id).all()
        
        category_ids = set()
        for item in items:
            # Try to get category from existing motorcycle
            if item.motorcycle_id:
                motorcycle = session.query(Motorcycles).filter(Motorcycles.id == item.motorcycle_id).first()
                if motorcycle and motorcycle.category_id:
                    category_ids.add(motorcycle.category_id)
            # Or get from rental item's price to match with category
            elif item.price_per_day:
                category = session.query(Catagory_Motorcycle).filter(
                    Catagory_Motorcycle.price_per_day == item.price_per_day
                ).first()
                if category:
                    category_ids.add(category.id)
        
        # Get all motorcycles from these categories
        motorcycles = []
        if category_ids:
            motorcycles_query = session.query(Motorcycles).filter(
                Motorcycles.category_id.in_(list(category_ids))
            ).all()
            
            for mc in motorcycles_query:
                motorcycles.append({
                    'id': mc.id,
                    'license_plate': mc.license_plate,
                    'category_name': mc.category.name if mc.category else '',
                    'status': mc.status,
                    'model_year': mc.model_year
                })
        else:
            # If no category found, get all motorcycles
            motorcycles_query = session.query(Motorcycles).all()
            for mc in motorcycles_query:
                motorcycles.append({
                    'id': mc.id,
                    'license_plate': mc.license_plate,
                    'category_name': mc.category.name if mc.category else '',
                    'status': mc.status,
                    'model_year': mc.model_year
                })
        
        # Get rental items info with all assigned motorcycles
        items_info = []
        for item in items:
            # Get all motorcycles assigned to this item (if any)
            assigned_motorcycles = []
            if item.motorcycle_id:
                mc = session.query(Motorcycles).filter(Motorcycles.id == item.motorcycle_id).first()
                if mc:
                    assigned_motorcycles.append({
                        'id': mc.id,
                        'license_plate': mc.license_plate
                    })
            
            items_info.append({
                'id': item.id,
                'motorcycle_id': item.motorcycle_id,
                'motorcycles': assigned_motorcycles,
                'motorcycle': {
                    'license_plate': item.motorcycle.license_plate if item.motorcycle else None
                } if item.motorcycle else None
            })
        
        return jsonify({
            'success': True,
            'motorcycles': motorcycles,
            'items': items_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    finally:
        session.close()


# ==================== PAYMENT MANAGEMENT ====================

@bp.route('/admin/payments')
def payments():
    """Quản lý giao dịch thanh toán"""
    session = get_db_session()
    try:
        # Get filter parameters
        status = request.args.get('status', '').strip()
        method = request.args.get('method', '').strip()
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = 20
        
        query = session.query(Payment).outerjoin(Rental)
        
        # Apply status filter
        if status:
            query = query.filter(Payment.payment_status == status)
        
        # Apply method filter
        if method:
            query = query.filter(Payment.payment_method == method)
        
        # Apply search filter
        if search:
            try:
                # Try to convert search to int for ID search
                search_int = int(search)
                query = query.filter(
                    (Payment.id == search_int) |
                    (Payment.payment_code.ilike(f'%{search}%')) |
                    (Payment.vnpay_transaction_id.ilike(f'%{search}%')) |
                    (Rental.id == search_int)
                )
            except ValueError:
                # If not a number, search in text fields
                query = query.filter(
                    (Payment.payment_code.ilike(f'%{search}%')) |
                    (Payment.vnpay_transaction_id.ilike(f'%{search}%'))
                )
        
        # Order by id desc (Payment doesn't have created_at in base model)
        query = query.order_by(desc(Payment.id))
        
        # Pagination
        total = query.count()
        payments_list = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Get statistics
        stats = {
            'total': session.query(func.count(Payment.id)).scalar(),
            'paid': session.query(func.count(Payment.id)).filter(Payment.payment_status == 'paid').scalar(),
            'pending': session.query(func.count(Payment.id)).filter(Payment.payment_status == 'pending').scalar(),
            'failed': session.query(func.count(Payment.id)).filter(Payment.payment_status == 'failed').scalar(),
            'total_amount': session.query(func.sum(Payment.amount)).filter(Payment.payment_status == 'paid').scalar() or Decimal('0')
        }
        
        return render_template('admin/payments.html',
                             payments=payments_list,
                             status=status,
                             method=method,
                             search=search,
                             page=page,
                             per_page=per_page,
                             total=total,
                             total_pages=(total + per_page - 1) // per_page,
                             stats=stats)
    finally:
        session.close()


@bp.route('/admin/payment/<int:payment_id>')
def payment_detail(payment_id):
    """Chi tiết giao dịch thanh toán"""
    session = get_db_session()
    try:
        payment = session.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            flash('Không tìm thấy giao dịch!', 'error')
            return redirect(url_for('admin.payments'))
        
        # Get rental
        rental = session.query(Rental).filter(Rental.id == payment.rental_id).first() if payment.rental_id else None
        
        # Get customer
        customer = None
        if rental and rental.customer_id:
            customer = session.query(Customer).filter(Customer.id == rental.customer_id).first()
        
        return render_template('admin/payment_detail.html',
                             payment=payment,
                             rental=rental,
                             customer=customer)
    finally:
        session.close()


def generate_order_id():
    """Generate unique order ID"""
    return datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))


@bp.route('/admin/rental/<int:rental_id>/calculate_payment', methods=['POST'])
def rental_calculate_payment(rental_id):
    """Tính toán số tiền còn lại phải thanh toán"""
    session = get_db_session()
    try:
        rental = session.query(Rental).filter(Rental.id == rental_id).first()
        if not rental:
            return jsonify({'success': False, 'message': 'Không tìm thấy đơn thuê!'}), 404
        
        if not rental.start_date:
            return jsonify({'success': False, 'message': 'Đơn thuê chưa có ngày bắt đầu!'}), 400
        
        data = request.get_json()
        actual_return_date_str = data.get('actual_return_date')
        
        if not actual_return_date_str:
            return jsonify({'success': False, 'message': 'Vui lòng chọn ngày trả thực tế!'}), 400
        
        # Parse actual return date
        try:
            actual_return_date = datetime.strptime(actual_return_date_str, '%Y-%m-%dT%H:%M')
        except:
            try:
                actual_return_date = datetime.strptime(actual_return_date_str, '%Y-%m-%d %H:%M:%S')
            except:
                return jsonify({'success': False, 'message': 'Định dạng ngày không hợp lệ!'}), 400
        
        # Calculate actual rental days
        if actual_return_date < rental.start_date:
            return jsonify({'success': False, 'message': 'Ngày trả không thể trước ngày bắt đầu!'}), 400
        
        # Calculate days (including start and end day)
        time_diff = actual_return_date - rental.start_date
        actual_days = max(1, (time_diff.days + 1))  # At least 1 day
        
        # Get all rental items with assigned motorcycles
        items = session.query(RentalItem).filter(
            RentalItem.rental_id == rental_id,
            RentalItem.motorcycle_id.isnot(None)
        ).all()
        
        if not items:
            return jsonify({'success': False, 'message': 'Chưa có xe nào được gán cho đơn thuê!'}), 400
        
        # Calculate total amount: sum of (price_per_day * actual_days) for each motorcycle
        total_amount = Decimal('0')
        for item in items:
            if item.price_per_day:
                total_amount += Decimal(str(item.price_per_day)) * actual_days
        
        # Get paid amount
        paid_amount = rental.paid_amount or Decimal('0')
        
        # Calculate remaining amount
        remaining_amount = max(Decimal('0'), total_amount - paid_amount)
        
        return jsonify({
            'success': True,
            'actual_days': actual_days,
            'total_amount': float(total_amount),
            'paid_amount': float(paid_amount),
            'remaining_amount': float(remaining_amount),
            'total_motorcycles': len(items)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    finally:
        session.close()


@bp.route('/admin/rental/<int:rental_id>/process_payment', methods=['POST'])
def rental_process_payment(rental_id):
    """Xử lý thanh toán và trả xe"""
    session = get_db_session()
    try:
        rental = session.query(Rental).filter(Rental.id == rental_id).first()
        if not rental:
            return jsonify({'success': False, 'message': 'Không tìm thấy đơn thuê!'}), 404
        
        data = request.get_json()
        actual_return_date_str = data.get('actual_return_date')
        payment_method = data.get('payment_method', 'cash')
        amount = Decimal(str(data.get('amount', 0)))
        
        if not actual_return_date_str:
            return jsonify({'success': False, 'message': 'Vui lòng chọn ngày trả thực tế!'}), 400
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Số tiền không hợp lệ!'}), 400
        
        # Parse actual return date
        try:
            actual_return_date = datetime.strptime(actual_return_date_str, '%Y-%m-%dT%H:%M')
        except:
            try:
                actual_return_date = datetime.strptime(actual_return_date_str, '%Y-%m-%d %H:%M:%S')
            except:
                return jsonify({'success': False, 'message': 'Định dạng ngày không hợp lệ!'}), 400
        
        # Calculate actual days
        if actual_return_date < rental.start_date:
            return jsonify({'success': False, 'message': 'Ngày trả không thể trước ngày bắt đầu!'}), 400
        
        time_diff = actual_return_date - rental.start_date
        actual_days = max(1, (time_diff.days + 1))
        
        # Get all rental items with assigned motorcycles
        items = session.query(RentalItem).filter(
            RentalItem.rental_id == rental_id,
            RentalItem.motorcycle_id.isnot(None)
        ).all()
        
        if not items:
            return jsonify({'success': False, 'message': 'Chưa có xe nào được gán cho đơn thuê!'}), 400
        
        # Calculate total amount
        total_amount = Decimal('0')
        for item in items:
            if item.price_per_day:
                total_amount += Decimal(str(item.price_per_day)) * actual_days
        
        # Update rental
        rental.actual_return_date = actual_return_date
        rental.rental_days = actual_days
        rental.total_amount = total_amount
        
        if payment_method == 'cash':
            # Cash payment - process immediately
            # Update paid amount
            current_paid = rental.paid_amount or Decimal('0')
            rental.paid_amount = current_paid + amount
            rental.payment_method = 'cash'
            
            # Create payment record
            payment = Payment(
                rental_id=rental.id,
                payment_code=f'CASH-{generate_order_id()}',
                amount=amount,
                payment_method='cash',
                payment_status='paid',
                payment_date=datetime.now()
            )
            session.add(payment)
            
            # Update rental status
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
            
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Thanh toán tiền mặt thành công! Xe đã được trả.'
            })
            
        elif payment_method == 'vnpay':
            # VNPay payment - create payment request
            # Generate order ID
            order_id = generate_order_id()
            
            # Get client IP
            ip_addr = get_client_ip(request)
            order_desc = f"Thanh toan don thue #{rental.id} - So tien con lai"
            
            # Get return URL - add admin parameter to know it's from admin
            base_return_url = os.getenv('VNPAY_RETURN_URL', f"http://{request.host}/payment/return")
            return_url = f"{base_return_url}?admin=1&rental_id={rental_id}"
            
            # Create VNPay payment request
            vnp = VNPay()
            payment_url = vnp.create_payment_request(
                order_id=order_id,
                amount=float(amount),
                order_desc=order_desc,
                ip_addr=ip_addr,
                bank_code='',
                return_url=return_url
            )
            
            # Create payment record (pending)
            payment = Payment(
                rental_id=rental.id,
                payment_code=order_id,
                amount=amount,
                payment_method='vnpay',
                payment_status='pending',
                vnpay_transaction_id=order_id
            )
            session.add(payment)
            
            # Store order_id in rental for reference (temporary)
            rental.vnpay_transaction_id = order_id
            
            session.commit()
            
            return jsonify({
                'success': True,
                'payment_url': payment_url,
                'message': 'Đang chuyển hướng đến VNPay...'
            })
        else:
            return jsonify({'success': False, 'message': 'Phương thức thanh toán không hợp lệ!'}), 400
            
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500
    finally:
        session.close()

