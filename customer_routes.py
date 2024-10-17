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