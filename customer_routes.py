from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
customers_collection = db['Customers']
customer_bp = Blueprint('customer_bp', __name__)
@customer_bp.route('/customer-list')
def customer_list():
    customers = customers_collection.find()
    return render_template('customer_list.html', customers=customers, enumerate=enumerate)


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
