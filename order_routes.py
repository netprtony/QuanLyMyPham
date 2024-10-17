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
    
@order_bp.route('/order/<order_id>')
def order_detail(order_id):
    order = orders_collection.find_one({"order_id": order_id})
    return render_template('order_detail.html', order=order)