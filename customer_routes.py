from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
import csv, json
import io
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
customers_collection = db['Customers']
orders_collection = db['Orders']
customer_bp = Blueprint('customer_bp', __name__)

@customer_bp.route('/customer-list')
def customer_list():
    customers = customers_collection.find()
    return render_template('customer_list.html', customers=customers, enumerate=enumerate)


@customer_bp.route('/edit-customer/<customer_id>',methods=['POST'])
def get_customer(customer_id):
    customer = customers_collection.find_one({"customer_id": customer_id})
    return render_template('edit_customer.html', customer=customer)

@customer_bp.route('/add-customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        # Lấy giá trị từ form với request.form.get() để tránh KeyError
        customer_id = request.form.get('customer_id')
        if not customer_id :
            return "Customer ID không được để trống", 400  # Thêm xử lý lỗi nếu cần
        if customers_collection.find_one({"customer_id": customer_id}) :
            return "Customer ID không được trùng", 400  # Thêm xử lý lỗi nếu cần
        # Lấy dữ liệu từ form
        customer_data = {
            "customer_id": customer_id,
            "name": request.form['name'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "gender": request.form['gender'],
            "age": int(request.form['age']),
            "address": {
                "street": request.form['street'],
                "city": request.form['city'],
                "postal_code": request.form['postal_code']
            },
            "preferred_delivery_location": "LOC001",
            "role": request.form['role']
        }
        # Thêm khách hàng vào MongoDB
        customers_collection.insert_one(customer_data)
        return redirect(url_for('customer_bp.customer_list'))
#Xóa-------------------------------------------------------
@customer_bp.route('/delete_customer/<customer_id>', methods=['POST'])
def delete_customer(customer_id):
    # Xóa khách hàng từ MongoDB
    result_customer = customers_collection.delete_one({'customer_id': customer_id})
    # Xóa tất cả đơn hàng của khách hàng
    if result_customer.deleted_count > 0 :
        return redirect(url_for('customer_bp.customer_list'))  # Chuyển hướng về danh sách khách hàng
    else:
        return "Không tìm thấy khách hàng với ID này", 404

#Sửa
@customer_bp.route('/update_customer', methods=['POST'])
def update_customer():
    customer_id = request.form['customer_id_edit']
    name = request.form['name_edit']
    gender = request.form['gender_edit']
    age = request.form['age_edit']
    street = request.form['street_edit']
    city = request.form['city_edit']
    postal_code = request.form['postal_code_edit']
    phone = request.form['phone_edit']
    email = request.form['email_edit']
    role = request.form['role_edit']

    # Cập nhật khách hàng trong MongoDB
    customers_collection.update_one(
        {'customer_id': customer_id},
        {'$set': {
            'name': name,
            'gender': gender,
            'age': age,
            'address.street': street,
            'address.city': city,
            'address.postal_code': postal_code,
            'phone': phone,
            'email': email,
            'role': role
        }}
    )
    return redirect(url_for('customer_bp.customer_list'))
#Tìm kiếm khách hàng theo mã
@customer_bp.route('/search_customer', methods=['GET'])
def search_customer():
    customer_id = request.args.get('customer_id')

    # Tìm khách hàng theo customer_id trong MongoDB
    customer = customers_collection.find_one({'customer_id': customer_id})

    if customer:
        # Nếu tìm thấy khách hàng, trả về trang kết quả
        return render_template('customer_list.html', customers=[customer])
    else:
        # Nếu không tìm thấy, có thể trả về một thông báo lỗi hoặc trang trắng
        return render_template('customer_list.html', customers=[], message="Không tìm thấy khách hàng")
    
@customer_bp.route('/import-csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        flash('Không có tệp nào được chọn')
        return redirect(request.url)

    file = request.files['file']
    
    if file.filename == '':
        flash('Không có tệp nào được chọn')
        return redirect(request.url)

    if file:
        try:
            # Mở tệp CSV trong chế độ văn bản
            with open(file.stream, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Xử lý từng hàng trong tệp CSV
                    customer_data = {
                        "customer_id": row['customer_id'],
                        "name": row['name'],
                        "email": row['email'],
                        "phone": row['phone'],
                        "gender": row['gender'],
                        "age": int(row['age']),
                        "address": {
                            "street": row['street'],
                            "city": row['city'],
                            "postal_code": row['postal_code']
                        },
                        "preferred_delivery_location": "LOC001",
                        "role": row['role']
                    }
                    customers_collection.insert_one(customer_data)
            flash('Dữ liệu đã được nhập thành công!')
        except Exception as e:
            flash(f'Lỗi khi nhập dữ liệu: {str(e)}')
            return redirect(request.url)
        
    return redirect(url_for('customer_bp.customer_list'))


@customer_bp.route('/import-json', methods=['POST'])
def import_json():
    if 'jsonFile' not in request.files:
        flash('Không tìm thấy file JSON', 'error')
        return redirect(url_for('customer_bp.customer_list'))

    file = request.files['jsonFile']

    if file.filename == '':
        flash('File không hợp lệ', 'error')
        return redirect(url_for('customer_bp.customer_list'))

    # Xử lý file JSON
    json_data = json.load(file.stream)
    
    for customer in json_data:
        customers_collection.insert_one(customer)

    flash('Dữ liệu JSON đã được import thành công', 'success')
    return redirect(url_for('customer_bp.customer_list'))


@customer_bp.route('/export-csv', methods=['GET'])
def export_csv():
    # Lấy danh sách khách hàng từ database
    customers = customers_collection.find()

    # Tạo một đối tượng BytesIO để ghi dữ liệu CSV vào
    output = io.BytesIO()

    # Tạo writer CSV từ BytesIO với delimiter là dấu phẩy
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Ghi tiêu đề cột
    writer.writerow(['STT', 'Mã', 'Tên', 'Giới tính', 'Tuổi', 'Địa chỉ', 'Số điện thoại', 'Email', 'Mức độ'])

    # Ghi dữ liệu khách hàng vào CSV
    for i, customer in enumerate(customers, 1):
        customer_dict = dict(customer)  # Chuyển đối tượng MongoDB thành từ điển

        writer.writerow([
            i,
            customer_dict.get('customer_id', ''),
            customer_dict.get('name', ''),
            customer_dict.get('gender', ''),
            customer_dict.get('age', ''),
            f"{customer_dict.get('address', {}).get('street', '')}, {customer_dict.get('address', {}).get('city', '')}, {customer_dict.get('address', {}).get('postal_code', '')}",
            customer_dict.get('phone', ''),
            customer_dict.get('email', ''),
            customer_dict.get('role', '')
        ])

    # Đặt con trỏ về đầu của BytesIO để đảm bảo đọc từ đầu
    output.seek(0)

    # Tạo response từ BytesIO
    response = make_response(output.getvalue().decode('utf-8'))
    response.headers['Content-Disposition'] = 'attachment; filename=customers.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response