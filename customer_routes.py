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

@customer_bp.route('/top-customers')
def top_customers():
    # Aggregation: Lọc các đơn hàng có trạng thái 'Delivered' và đếm số lần giao thành công cho mỗi khách hàng
    pipeline = [
        {"$match": {"status": "Delivered"}},
        {"$group": {
            "_id": "$customer_id",
            "total_deliveries": {"$sum": 1}
        }},
        {"$match": {"total_deliveries": {"$gt": 0}}},  # Chỉ lấy những khách hàng có giao hàng
        {"$lookup": {
            "from": "Customers",
            "localField": "_id",
            "foreignField": "customer_id",
            "as": "customer_info"
        }},
        {"$unwind": "$customer_info"},  # Giải nén thông tin khách hàng từ mảng
        {"$project": {
            "_id": 0,
            "customer_id": "$_id",
            "name": "$customer_info.name",
            "phone": "$customer_info.phone",
            "address": "$customer_info.address.street",
            "total_deliveries": 1
        }},
        {"$sort": {"total_deliveries": -1}}  # Sắp xếp theo số lần giao hàng giảm dần
    ]

    top_customers = list(orders_collection.aggregate(pipeline))
    return render_template('top_customers.html', customers=top_customers)

@customer_bp.route('/customer-orders/<customer_id>')
def get_customer_orders(customer_id):
    # Truy vấn danh sách đơn hàng của khách hàng từ collection 'Orders'
    orders = orders_collection.find({"customer_id": customer_id, "status": "Delivered"})
    return render_template('customer_orders.html', orders=orders, customer_id=customer_id)


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
    