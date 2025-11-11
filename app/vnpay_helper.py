"""
VNPay helper - Chuyển đổi từ Django vnpay_python
"""
import hashlib
import hmac
import urllib.parse
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class VNPay:
    """VNPay payment integration helper - Ported from Django"""
    requestData = {}
    responseData = {}
    
    def __init__(self):
        # Load config from environment variables
        self.tmn_code = os.getenv('VNPAY_TMN_CODE', '08XB68MP')
        self.hash_secret = os.getenv('VNPAY_HASH_SECRET') or os.getenv('VNPAY_HASH_SECRET_KEY', 'J387G5VO8FUMTRBMPSANSJXOSMCNLKBK')
        self.payment_url = os.getenv('VNPAY_PAYMENT_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
        self.api_url = os.getenv('VNPAY_API_URL', 'https://sandbox.vnpayment.vn/merchant_webapi/api/transaction')
        self.return_url = os.getenv('VNPAY_RETURN_URL', 'http://localhost:5000/payment/return')
    
    def get_payment_url(self, vnpay_payment_url=None, secret_key=None):
        """Generate VNPay payment URL"""
        if vnpay_payment_url is None:
            vnpay_payment_url = self.payment_url
        if secret_key is None:
            secret_key = self.hash_secret
            
        inputData = sorted(self.requestData.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self._hmacsha512(secret_key, queryString)
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key=None):
        """Validate VNPay response signature"""
        if secret_key is None:
            secret_key = self.hash_secret
            
        vnp_SecureHash = self.responseData.get('vnp_SecureHash', '')
        if not vnp_SecureHash:
            return False
            
        # Remove hash params
        response_data_copy = dict(self.responseData)
        if 'vnp_SecureHash' in response_data_copy:
            response_data_copy.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in response_data_copy:
            response_data_copy.pop('vnp_SecureHashType')

        inputData = sorted(response_data_copy.items())
        hasData = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
        hashValue = self._hmacsha512(secret_key, hasData)

        print('Validate debug, HashData:' + hasData + "\n HashValue:" + hashValue + "\nInputHash:" + vnp_SecureHash)

        return vnp_SecureHash == hashValue

    @staticmethod
    def _hmacsha512(key, data):
        """Generate HMAC SHA512 hash"""
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()
    
    def create_payment_request(self, order_id, amount, order_desc, ip_addr, 
                              order_type='other', bank_code='', locale='vn', return_url=None):
        """Create payment request data"""
        if return_url is None:
            return_url = self.return_url
            
        self.requestData = {}
        self.requestData['vnp_Version'] = '2.1.0'
        self.requestData['vnp_Command'] = 'pay'
        self.requestData['vnp_TmnCode'] = self.tmn_code
        self.requestData['vnp_Amount'] = int(amount * 100)  # Convert to cents
        self.requestData['vnp_CurrCode'] = 'VND'
        self.requestData['vnp_TxnRef'] = str(order_id)
        self.requestData['vnp_OrderInfo'] = order_desc
        self.requestData['vnp_OrderType'] = order_type
        
        if locale and locale != '':
            self.requestData['vnp_Locale'] = locale
        else:
            self.requestData['vnp_Locale'] = 'vn'
        
        if bank_code and bank_code != "":
            self.requestData['vnp_BankCode'] = bank_code
        
        self.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        self.requestData['vnp_IpAddr'] = ip_addr
        self.requestData['vnp_ReturnUrl'] = return_url
        
        return self.get_payment_url()


def get_client_ip(request):
    """Get client IP address from Flask request"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
    return ip

