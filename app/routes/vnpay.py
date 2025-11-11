"""
VNPay routes - Tích hợp VNPay vào Flask app
"""
from flask import jsonify, request, redirect, url_for
from datetime import datetime
from . import bp
from app.vnpay_helper import VNPay, get_client_ip


@bp.route('/api/vnpay/create_payment', methods=['POST'])
def api_create_payment():
    """API endpoint để tạo payment URL"""
    try:
        data = request.get_json()
        
        # Get data from request
        order_id = data.get('order_id')
        amount = float(data.get('amount', 0))
        order_desc = data.get('order_desc', '')
        order_type = data.get('order_type', 'other')
        bank_code = data.get('bank_code', '')
        language = data.get('language', 'vn')
        ip_addr = data.get('ip_addr', get_client_ip(request))
        return_url = data.get('return_url')
        
        if not order_id or amount <= 0:
            return jsonify({
                'success': False,
                'message': 'Thiếu thông tin order_id hoặc amount'
            }), 400
        
        # Build URL Payment
        vnp = VNPay()
        payment_url = vnp.create_payment_request(
            order_id=order_id,
            amount=amount,
            order_desc=order_desc,
            ip_addr=ip_addr,
            order_type=order_type,
            bank_code=bank_code,
            locale=language,
            return_url=return_url
        )
        
        return jsonify({
            'success': True,
            'payment_url': payment_url,
            'order_id': order_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500


@bp.route('/api/vnpay/payment_callback', methods=['GET'])
def api_payment_callback():
    """API endpoint để xử lý callback từ VNPay - trả về JSON"""
    try:
        # Get all vnp_* parameters
        input_data = {k: v for k, v in request.args.items() if k.startswith('vnp_')}
        
        if not input_data:
            return jsonify({
                'success': False,
                'message': 'Invalid request'
            }), 400
        
        vnp = VNPay()
        vnp.responseData = input_data
        
        order_id = input_data.get('vnp_TxnRef', '')
        amount = int(input_data.get('vnp_Amount', 0)) / 100
        order_desc = input_data.get('vnp_OrderInfo', '')
        vnp_TransactionNo = input_data.get('vnp_TransactionNo', '')
        vnp_ResponseCode = input_data.get('vnp_ResponseCode', '')
        vnp_TmnCode = input_data.get('vnp_TmnCode', '')
        vnp_PayDate = input_data.get('vnp_PayDate', '')
        vnp_BankCode = input_data.get('vnp_BankCode', '')
        vnp_CardType = input_data.get('vnp_CardType', '')
        vnp_TransactionStatus = input_data.get('vnp_TransactionStatus', '')
        
        if vnp.validate_response():
            # Determine success
            is_success = False
            if vnp_ResponseCode:
                is_success = (vnp_ResponseCode == '00')
            elif vnp_TransactionStatus:
                is_success = (vnp_TransactionStatus == '00')
            else:
                is_success = (vnp_TransactionNo and vnp_TransactionNo != '0')
            
            return jsonify({
                'success': True,
                'valid': True,
                'payment_success': is_success,
                'order_id': order_id,
                'amount': amount,
                'order_desc': order_desc,
                'transaction_no': vnp_TransactionNo,
                'response_code': vnp_ResponseCode,
                'transaction_status': vnp_TransactionStatus,
                'bank_code': vnp_BankCode,
                'card_type': vnp_CardType,
                'pay_date': vnp_PayDate,
                'tmn_code': vnp_TmnCode
            })
        else:
            return jsonify({
                'success': True,
                'valid': False,
                'message': 'Invalid Signature'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

