/**
 * ================================================
 * RENTAL MODAL JAVASCRIPT
 * JavaScript cho chức năng đặt thuê xe máy
 * ================================================
 */

// Global variable để lưu giá xe hiện tại
let currentMotorcyclePrice = 0;

/**
 * Mở modal đặt thuê xe
 * @param {number} motorcycleId - ID của xe máy
 * @param {string} motorcycleName - Tên xe máy
 * @param {number} pricePerDay - Giá thuê mỗi ngày
 */
function openRentalModal(motorcycleId, motorcycleName, pricePerDay) {
    currentMotorcyclePrice = pricePerDay;
    
    // Cập nhật thông tin xe vào modal
    document.getElementById('motorcycleId').value = motorcycleId;
    document.getElementById('modalMotorcycleName').textContent = 'Thuê Xe Máy ' + motorcycleName;
    document.getElementById('modalMotorcyclePrice').textContent = formatCurrency(pricePerDay) + ' VND/Ngày';
    
    // Reset form về giá trị mặc định
    document.getElementById('quantity').value = 1;
    document.getElementById('days').value = 1;
    
    // Set min date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start_date').min = today;
    document.getElementById('end_date').min = today;
    
    // Reset các trường thông tin cá nhân
    document.getElementById('rentalForm').reset();
    document.getElementById('motorcycleId').value = motorcycleId;
    document.getElementById('quantity').value = 1;
    document.getElementById('days').value = 1;
    document.getElementById('start_date').min = today;
    document.getElementById('end_date').min = today;
    
    // Clear image previews
    document.getElementById('preview-front').innerHTML = '';
    document.getElementById('preview-front').classList.remove('has-image');
    document.getElementById('preview-back').innerHTML = '';
    document.getElementById('preview-back').classList.remove('has-image');
    
    // Tính toán giá ban đầu
    calculateDeposit();
    
    // Hiển thị modal
    document.getElementById('rentalModal').style.display = 'block';
    document.body.style.overflow = 'hidden'; // Ngăn scroll trang khi modal mở
}

/**
 * Đóng modal đặt thuê xe
 */
function closeRentalModal() {
    document.getElementById('rentalModal').style.display = 'none';
    document.body.style.overflow = 'auto'; // Cho phép scroll lại
}

/**
 * Format số thành định dạng tiền tệ Việt Nam
 * @param {number} amount - Số tiền cần format
 * @returns {string} Chuỗi số đã được format
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount);
}

/**
 * Cập nhật số ngày thuê dựa trên ngày bắt đầu và ngày kết thúc
 */
function updateDays() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const daysInput = document.getElementById('days');
    
    if (startDateInput.value && endDateInput.value) {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (endDate >= startDate) {
            const diffTime = Math.abs(endDate - startDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // +1 để bao gồm cả ngày cuối
            daysInput.value = diffDays;
            calculateDeposit();
        } else {
            daysInput.value = 1;
            alert('Ngày kết thúc phải sau ngày bắt đầu!');
        }
    }
}

/**
 * Tính toán và hiển thị tổng giá thuê và tiền đặt cọc
 */
function calculateDeposit() {
    const quantity = parseInt(document.getElementById('quantity').value) || 0;
    const days = parseInt(document.getElementById('days').value) || 0;
    
    // Tính tổng giá thuê
    const totalPrice = currentMotorcyclePrice * quantity * days;
    
    // Tính tiền đặt cọc (50% tổng giá)
    const depositAmount = totalPrice * 0.5;
    
    // Cập nhật UI
    document.getElementById('totalPrice').textContent = formatCurrency(totalPrice) + ' VND';
    document.getElementById('depositAmount').textContent = formatCurrency(depositAmount) + ' VND';
}

/**
 * Preview ảnh khi người dùng chọn file
 * @param {HTMLInputElement} input - Input file element
 * @param {string} previewId - ID của div preview
 */
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = '<img src="' + e.target.result + '" alt="Preview">';
            preview.classList.add('has-image');
        };
        
        reader.readAsDataURL(input.files[0]);
    } else {
        preview.innerHTML = '';
        preview.classList.remove('has-image');
    }
}

/**
 * Xử lý khi form được submit
 */
function handleRentalFormSubmit(event) {
    event.preventDefault();
    
    // Validate form
    if (!validateRentalForm()) {
        return;
    }
    
    // Disable submit button to prevent double submission
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Đang xử lý...';
    
    // Create FormData from form
    const formData = new FormData(event.target);
    
    // Send data to server
    fetch('/api/rental/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect to VNPay payment page
            window.location.href = data.payment_url;
        } else {
            // Show error message
            alert('Lỗi: ' + (data.message || 'Có lỗi xảy ra khi xử lý đơn hàng!'));
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Lỗi kết nối! Vui lòng thử lại sau.');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

/**
 * Validate form trước khi submit
 * @returns {boolean} True nếu form hợp lệ
 */
function validateRentalForm() {
    const requiredFields = [
        'start_date',
        'end_date',
        'full_name',
        'phone',
        'date_of_birth',
        'hometown',
        'address',
        'citizen_id',
        'citizen_id_front_image',
        'citizen_id_back_image'
    ];
    
    for (let fieldName of requiredFields) {
        const field = document.getElementById(fieldName);
        if (!field || !field.value) {
            alert('Vui lòng điền đầy đủ thông tin bắt buộc!');
            field?.focus();
            return false;
        }
    }
    
    // Validate dates
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        if (end < start) {
            alert('Ngày kết thúc phải sau ngày bắt đầu!');
            document.getElementById('end_date').focus();
            return false;
        }
    }
    
    // Validate phone number (basic)
    const phone = document.getElementById('phone').value;
    if (!/^[0-9]{10,11}$/.test(phone.replace(/\s/g, ''))) {
        alert('Số điện thoại không hợp lệ! Vui lòng nhập số điện thoại 10-11 chữ số.');
        document.getElementById('phone').focus();
        return false;
    }
    
    // Validate email format if provided
    const email = document.getElementById('email').value;
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert('Email không hợp lệ!');
        document.getElementById('email').focus();
        return false;
    }
    
    // Validate citizen ID (basic - 9 or 12 digits)
    const citizenId = document.getElementById('citizen_id').value;
    if (!/^[0-9]{9,12}$/.test(citizenId.replace(/\s/g, ''))) {
        alert('Số CCCD/CMND không hợp lệ! Vui lòng nhập 9 hoặc 12 chữ số.');
        document.getElementById('citizen_id').focus();
        return false;
    }
    
    return true;
}

/**
 * Khởi tạo các event listeners khi DOM đã load xong
 */
document.addEventListener('DOMContentLoaded', function() {
    // Event listener cho form submit
    const rentalForm = document.getElementById('rentalForm');
    if (rentalForm) {
        rentalForm.addEventListener('submit', handleRentalFormSubmit);
    }
    
    // Event listener để đóng modal khi click bên ngoài
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('rentalModal');
        if (event.target === modal) {
            closeRentalModal();
        }
    });
    
    // Event listener cho phím ESC để đóng modal
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modal = document.getElementById('rentalModal');
            if (modal && modal.style.display === 'block') {
                closeRentalModal();
            }
        }
    });
});

// Export functions để có thể sử dụng ở nơi khác nếu cần
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        openRentalModal,
        closeRentalModal,
        formatCurrency,
        calculateDeposit
    };
}
