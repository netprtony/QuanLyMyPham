from flask import Blueprint, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
customers_collection = db['Customers']
customer_bp = Blueprint('customer_bp', __name__)

@customer_bp.route('/customer-list')
def customer_list():
    customers = customers_collection.find()
    return render_template('customer_list.html', customers=customers, enumerate=enumerate)

@customer_bp.route('/customer/<customer_id>')
def get_customer(customer_id):
    customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
    return render_template('customer_list.html', customer=customer)

@customer_bp.route('/add-customer', methods=['POST'])
def add_customer():
    if request.method == 'POST':
        # Lấy giá trị từ form với request.form.get() để tránh KeyError
        customer_id = request.form.get('customer_id')
        if not customer_id:
            return "Customer ID không được để trống", 400  # Thêm xử lý lỗi nếu cần
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
    result = customers_collection.delete_one({'customer_id': customer_id})

    if result.deleted_count > 0:
        return redirect(url_for('customer_bp.customer_list'))  # Chuyển hướng về danh sách khách hàng
    else:
        return "Không tìm thấy khách hàng với ID này", 404
#Sửa
@customer_bp.route('/edit_customer/<customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    if request.method == 'GET':
        # Lấy thông tin khách hàng dựa trên customer_id
        customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
        if customer:
            return render_template('edit_customer.html', customer=customer)
        else:
            return "Khách hàng không tồn tại", 404

    if request.method == 'POST':
        # Cập nhật thông tin khách hàng
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        age = request.form['age']
        street = request.form['street']
        city = request.form['city']
        postal_code = request.form['postal_code']
        preferred_delivery_location = request.form['preferred_delivery_location']
        role = request.form['role']
        # Cập nhật thông tin khách hàng trong MongoDB
        customers_collection.update_one(
            {"_id": ObjectId(customer_id)},
            {
                "$set": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "age": age,
                    "gender" : gender,
                    "address.street": street,
                    "address.city": city,
                    "address.postal_code": postal_code,
                    "preferred_delivery_location": preferred_delivery_location,
                    "role": role
                }
            }
        )
        return redirect(url_for('customer_bp.customer_list'))