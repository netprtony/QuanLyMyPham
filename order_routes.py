from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
orders_collection = db['Orders']
customers_collection = db['Customers']
# Tạo một Blueprint cho các route của đơn hàng
order_bp = Blueprint('order_bp', __name__)




@order_bp.route('/order-list')
def order_list():
    orders = orders_collection.find()
    return render_template('order_list.html', orders=orders, enumerate=enumerate)
    
@order_bp.route('/order-detail/<order_id>')
def order_detail(order_id):
    # Tìm đơn hàng dựa trên order_id
    order = orders_collection.find_one({"order_id": order_id})
    
    if not order:
        return "Đơn hàng không tồn tại", 404  # Thông báo lỗi nếu không tìm thấy đơn hàng

    # Truy vấn khách hàng liên quan đến đơn hàng
    customer = customers_collection.find_one({"customer_id": order['customer_id']})

    # Gửi dữ liệu đơn hàng và thông tin khách hàng vào template
    return render_template('order_detail.html', order=order, customer=customer)