from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
from collections import defaultdict
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
products_collection = db['Products']
supplier_collection = db['Suppliers']
orders_collection = db['Orders']
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


@product_bp.route('/update-product', methods=['POST'])
def update_product():
    # Lấy giá trị từ form
    product_id_edit = request.form['product_id_edit']
    name_edit = request.form['name_edit']
    category_edit = request.form['category_edit']
    brand_edit = request.form['brand_edit']
    price_edit = int(request.form['price_edit'])
    stock_edit = int(request.form['stock_edit'])
    supplier_id_edit = request.form['supplier_id_edit']
    description_edit = request.form['description_edit']

    # Cập nhật sản phẩm trong MongoDB
    products_collection.update_one(
        {'product_id': product_id_edit},
        {'$set': {
            'name': name_edit,
            'category': category_edit,
            'brand': brand_edit,
            'price': price_edit,
            'stock': stock_edit,
            'supplier_id': supplier_id_edit,
            'description': description_edit
        }}
    )
    return redirect(url_for('product_bp.product_list'))

@product_bp.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    # Xóa khách hàng từ MongoDB
    result = products_collection.delete_one({'product_id': product_id})

    if result.deleted_count > 0:
        return redirect(url_for('product_bp.product_list'))  # Chuyển hướng về danh sách mỹ phẩm
    else:
        return "Không tìm thấy sản phẩm với ID này", 404
    

@product_bp.route('/products', methods=['GET'])
def list_products_by_category():
    # Lấy chủng loại từ query parameter
    category = request.args.get('category')

    # Kiểm tra nếu có chủng loại được cung cấp
    if category:
        # Lọc sản phẩm theo chủng loại
        products = products_collection.find({"category": category})
    else:
        # Nếu không có chủng loại được cung cấp, trả về tất cả sản phẩm
        products = products_collection.find()

    # Chuyển đổi kết quả thành danh sách
    products_list = list(products)

    return render_template('product_list.html', products=products_list)

@product_bp.route('/product-list')
def product_list():
    filter_type = request.args.get('filter')

    if filter_type == 'most_selling':
        # Lọc sản phẩm bán nhiều nhất
        products = list(orders_collection.aggregate([
            {"$unwind": "$products_ordered"},
            {"$group": {
                "_id": "$products_ordered.product_name",
                "total_quantity_sold": {"$sum": "$products_ordered.quantity"}
            }},
            {"$sort": {"total_quantity_sold": -1}},
            {"$limit": 1}
        ]))
    elif filter_type == 'least_selling':
        # Lọc sản phẩm bán ít nhất
        products = list(orders_collection.aggregate([
            {"$unwind": "$products_ordered"},
            {"$group": {
                "_id": "$products_ordered.product_name",
                "total_quantity_sold": {"$sum": "$products_ordered.quantity"}
            }},
            {"$sort": {"total_quantity_sold": 1}},
            {"$limit": 1}
        ]))
    elif filter_type == 'unsold':
        # Lọc sản phẩm chưa được mua
        sold_products = orders_collection.aggregate([
            {"$unwind": "$products_ordered"},
            {"$group": {
                "_id": "$products_ordered.product_name"
            }}
        ])
        products = list(products_collection.find({
            "name": {"$nin": [product["_id"] for product in sold_products]}
        }))
    else:
        # Hiển thị tất cả sản phẩm
        products = list(products_collection.find())

    return render_template('product_list.html', products=products)