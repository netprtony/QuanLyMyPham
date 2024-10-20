from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
suppliers_collection = db['Suppliers']
product_collection = db['Products']
supplier_bp = Blueprint('supplier_bp', __name__)

@supplier_bp.route('/supplier-list')
def supplier_list():
    suppliers = suppliers_collection.find()
    products = product_collection.find()
    return render_template('supplier_list.html', suppliers=suppliers, enumerate=enumerate)

@supplier_bp.route('/add-supplier', methods=['POST'])
def add_supplier():
    if request.method == 'POST':
        # Lấy giá trị từ form với request.form.get() để tránh KeyError
        supplier_id = request.form.get('supplier_id')
        if not supplier_id:
            return "Supplier ID không được để trống", 400  # Thêm xử lý lỗi nếu cần

        # Lấy dữ liệu từ form
        supplier_data = {
            "supplier_id": supplier_id,
            "name": request.form['name'],
            "contact_info": {
                "phone": request.form['phone'],
                "email": request.form['email'],
                "address": request.form['address']
            }
        }

        # Thêm nhà cung cấp vào MongoDB
        suppliers_collection.insert_one(supplier_data)
        return redirect(url_for('supplier_bp.supplier_list'))
    
#Xóa--------------------------------------------------------------
@supplier_bp.route('/delete_supplier/<supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    # Xóa khách hàng từ MongoDB
    result_supplier = suppliers_collection.delete_one({'supplier_id': supplier_id})
    # Xóa tất cả đơn hàng của khách hàng
    if result_supplier.deleted_count > 0 :
        return redirect(url_for('supplier_bp.supplier_list'))  # Chuyển hướng về danh sách khách hàng
    else:
        return "Không tìm thấy khách hàng với ID này", 404