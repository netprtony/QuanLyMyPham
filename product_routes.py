from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
products_collection = db['Products']
# Tạo một Blueprint cho các route của đơn hàng
product_bp = Blueprint('product_bp', __name__)
@product_bp.route('/product-list')
def product_list():
    products = products_collection.find()
    return render_template('product_list.html', products=products, enumerate=enumerate)

@product_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        product_type = request.form['product_type']
        price = request.form['price']
        quantity = request.form['quantity']

        # Thêm dữ liệu sản phẩm vào MongoDB
        products_collection.insert_one({
            'name': name,
            'brand': brand,
            'product_type': product_type,
            'price': price,
            'quantity': quantity
        })
        return redirect(url_for('product_list'))
    return render_template('add_product.html')

@product_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    # Lấy dữ liệu sản phẩm từ MongoDB
    product = products_collection.find_one({'_id': product_id})
    if request.method == 'POST':
        product['name'] = request.form['name']
        product['brand'] = request.form['brand']
        product['product_type'] = request.form['product_type']
        product['price'] = request.form['price']
        product['quantity'] = request.form['quantity']
        # Cập nhật dữ liệu sản phẩm trong MongoDB
        products_collection.update_one({'_id': product_id}, {'$set': product})
        return redirect(url_for('product_list'))
    return render_template('edit_product.html', product=product)

@product_bp.route('/delete-product/<int:product_id>')
def delete_product(product_id):
    # Xóa dữ liệu sản phẩm trong MongoDB
    products_collection.delete_one({'_id': product_id})
    return redirect(url_for('product_list'))