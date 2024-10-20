from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
products_collection = db['Products']
supplier_collection = db['Suppliers']
# Tạo một Blueprint cho các route của đơn hàng
product_bp = Blueprint('product_bp', __name__)
@product_bp.route('/product-list')
def product_list():
    suppliers = supplier_collection.find()
    products = products_collection.find()
    return render_template('product_list.html', products=products, suppliers=suppliers)

@product_bp.route('/add-product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        # Lấy giá trị từ form với request.form.get() để tránh KeyError
        product_id = request.form.get('product_id')
        if not product_id:
            return "Product ID không được để trống", 400  # Xử lý lỗi nếu thiếu mã sản phẩm

        # Lấy dữ liệu từ form
        product_data = {
            "product_id": product_id,
            "name": request.form['name'],
            "category": request.form['category'],
            "brand": request.form['brand'],
            "price": int(request.form['price']),
            "stock": int(request.form['stock']),
            "supplier_id": request.form['supplier_id'],
            "description": request.form['description']
        }

        # Thêm sản phẩm vào MongoDB
        products_collection.insert_one(product_data)
        return redirect(url_for('product_bp.product_list'))


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

@product_bp.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    # Xóa khách hàng từ MongoDB
    result = products_collection.delete_one({'product_id': product_id})

    if result.deleted_count > 0:
        return redirect(url_for('product_bp.product_list'))  # Chuyển hướng về danh sách mỹ phẩm
    else:
        return "Không tìm thấy sản phẩm với ID này", 404