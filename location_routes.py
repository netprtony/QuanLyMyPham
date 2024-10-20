from flask import Blueprint, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
location_collection = db['Deliveries']
location_bp = Blueprint('location_bp', __name__)

@location_bp.route('/location-list')
def location_list():
    locations = location_collection.find()
    return render_template('location_list.html', locations=locations, enumerate=enumerate)

#Thêm
@location_bp.route('/add-location', methods=['POST'])
def add_location():
    if request.method == 'POST':
        # Lấy giá trị từ form với request.form.get() để tránh KeyError
        location_id = request.form.get('location_id')
        if not location_id:
            return "location ID không được để trống", 400  # Thêm xử lý lỗi nếu cần
        # Lấy dữ liệu từ form
        location_data = {
            "location_id": location_id,
            "address": request.form['address'],
            "city": request.form['city'],
            "postal_code": request.form['postal_code'],
            "country": request.form['country'],
            "contact_number": request.form['contact_number'],
            "type": request.form['type']
        }
        # Thêm khách hàng vào MongoDB
        location_collection.insert_one(location_data)
        return redirect(url_for('location_bp.location_list'))

#Sửa---------------------------------------------------------
@location_bp.route('/update_location', methods=['POST'])
def update_location():
    location_id_edit = request.form['location_id_edit']
    city_edit = request.form['city_edit']
    postal_code_edit = request.form['postal_code_edit']
    address_edit = request.form['address_edit']
    country_edit = request.form['country_edit']
    contact_number_edit = request.form['contact_number_edit']
    type_edit = request.form['type_edit']

    # Cập nhật khách hàng trong MongoDB
    location_collection.update_one(
        {'location_id': location_id_edit},
        {'$set': {
            'city': city_edit,
            'postal_code': postal_code_edit,
            'address': address_edit,
            'country': country_edit,
            'contact_number': contact_number_edit,
            'type': type_edit
        }}
    )
    return redirect(url_for('location_bp.location_list'))

    
#Xóa-------------------------------------------------------
@location_bp.route('/delete_location/<location_id>', methods=['POST'])
def delete_location(location_id):
    # Xóa khách hàng từ MongoDB
    result = location_collection.delete_one({'location_id': location_id})

    if result.deleted_count > 0:
        return redirect(url_for('location_bp.location_list'))  # Chuyển hướng về danh sách khách hàng
    else:
        return "Không tìm thấy khách hàng với ID này", 404
    

@location_bp.route('/filter-locations', methods=['GET'])
def filter_locations():
    city = request.args.get('city-select')
    if city:
        filtered_locations = location_collection.find({"city": city})
    else:
        filtered_locations = location_collection.find()  # Nếu không có thành phố, lấy tất cả

    return render_template('location_list.html', locations=filtered_locations)