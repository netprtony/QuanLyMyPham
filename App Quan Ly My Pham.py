from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017')
db = client['QL_CosmeticsStore']
customers_collection = db['Customer']
delivery_collection = db['Delivery']
products_collection = db['Product']
order_collection = db['Order']
locations_collection = db['Delivery']


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thiết lập secret_key cho session

# Danh sách khách hàng và địa điểm lưu trữ tạm thời
customers = []
locations = []  # Danh sách địa điểm giao hàng
products = []
delivery_methods = ['Giao hàng tiết kiệm', 'Giao hàng nhanh', 'Giao hàng tận nơi', 'Chọn địa điểm nhận hàng']
@app.route('/')
def home():
    username = session.get('username', 'Người Dùng A')  # Lấy username từ session
    return render_template('index.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra thông tin đăng nhập (nên sử dụng cơ sở dữ liệu)
        if username == 'admin' and password == 'password':  # Ví dụ đơn giản
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Sai tên đăng nhập hoặc mật khẩu')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     # ... (code của route '/register') ...

# @app.route('/success')
# def success():
#     return render_template('success.html', customers=customers)

####custormer####

@app.route('/customer-list')
def customer_list():
    # Lấy dữ liệu khách hàng từ MongoDB
    customers = list(customers_collection.find())
    return render_template('customer_list.html', customers=customers, enumerate=enumerate)

# ... (các route và hàm khác) ...

@app.route('/add-customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        email = request.form['email']

        # Thêm dữ liệu khách hàng vào MongoDB
        customers_collection.insert_one({
            'name': name,
            'address': address,
            'phone_number': phone_number,
            'email': email
        })
        return redirect(url_for('customer_list'))
    return render_template('add_customer.html')
# sửa khách hàng
# @app.route('/edit-customer/<int:customer_id>', methods=['GET', 'POST'])
# def edit_customer(customer_id):
#     # Lấy dữ liệu khách hàng từ MongoDB
#     customer = customers_collection.find_one({'_id': customer_id})
#     if request.method == 'POST':
#         customer['name'] = request.form['name']
#         customer['address'] = request.form['address']
#         customer['phone_number'] = request.form['phone_number']
#         customer['email'] = request.form['email']
#         # Cập nhật dữ liệu khách hàng trong MongoDB
#         customers_collection.update_one({'_id': customer_id}, {'$set': customer})
#         return redirect(url_for('customer_list'))
#     return render_template('edit_customer.html', customer=customer)

# @app.route('/delete_customer/<int:customer_id>', methods=['POST'])
# def delete_customer(customer_id):
#     # Xóa dữ liệu khách hàng trong MongoDB
#     customers_collection.delete_one({'_id': customer_id})
#     return 'Success'

@app.route('/edit_customer')
def edit_customer_page():
    return render_template('edit_customer.html')

@app.route('/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = customers_collection.find_one({"_id": customer_id})
    if customer:
        return jsonify(customer), 200
    else:
        return jsonify({"error": "Khách hàng không tồn tại."}), 404
    

@app.route('/update_customer/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()  # Lấy dữ liệu từ yêu cầu
    updated_data = {
        "name": data.get("name"),
        "address": data.get("address"),
        "phone": data.get("phone"),
        "email": data.get("email")
    }
    
    result = customers_collection.update_one({"_id": customer_id}, {"$set": updated_data})
    if result.modified_count > 0:
        return jsonify({"message": "Thông tin khách hàng đã được cập nhật thành công."}), 200
    else:
        return jsonify({"message": "Không tìm thấy khách hàng hoặc không có thay đổi."}), 404

# xóa khách hàng
@app.route('/delete_customer/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    result = customers_collection.delete_one({"_id": customer_id})  # Sử dụng ObjectId nếu ID là ObjectId
    if result.deleted_count > 0:
        return jsonify({"message": "Khách hàng đã được xóa thành công."}), 200
    else:
        return jsonify({"message": "Không tìm thấy khách hàng."}), 404

#####Products###
@app.route('/products')
def product_list():
    # Lấy dữ liệu sản phẩm từ MongoDB
    products = list(products_collection.find())
    return render_template('product_list.html', products=products, enumerate=enumerate)

# ... (các route và hàm khác) ...

@app.route('/add-product', methods=['GET', 'POST'])
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

@app.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
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

@app.route('/delete-product/<int:product_id>')
def delete_product(product_id):
    # Xóa dữ liệu sản phẩm trong MongoDB
    products_collection.delete_one({'_id': product_id})
    return redirect(url_for('product_list'))

#####location###
@app.route('/locations')
def location_list():
    # Lấy danh sách địa điểm từ MongoDB
    locations = list(delivery_collection.find())
    return render_template('location_list.html', locations=locations, enumerate=enumerate)

@app.route('/add-location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_name = request.form['location_name']
        address = request.form['address']
        note = request.form['note']

        result = locations_collection.insert_one({
            'location_name': location_name,
            'address': address,
            'note': note
        })
        print(f"Inserted {result.inserted_id} document")  # Thêm log để kiểm tra
        return redirect(url_for('location_list'))
    return render_template('add_location.html')

@app.route('/edit-location/<int:location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = locations[location_id]
    if request.method == 'POST':
        location['location_name'] = request.form['location_name']
        location['address'] = request.form['address']
        location['note'] = request.form['note']
        return redirect(url_for('location_list'))
    return render_template('edit_location.html', location=location)

@app.route('/delete-location/<int:location_id>')
def delete_location(location_id):
    del locations[location_id]
    return redirect(url_for('location_list'))

####delivery####
@app.route('/delivery', methods=['GET', 'POST'])
def delivery():
    if request.method == 'POST':
        # Xử lý dữ liệu từ form
        selected_location = request.form['selected_location']
        selected_delivery_method = request.form['selected_delivery_method']
        # ... (xử lý thêm các dữ liệu khác) ...

        # Thêm thông tin đơn hàng vào cơ sở dữ liệu
        # ...

        return redirect(url_for('delivery_tracking'))  # Chuyển hướng đến trang theo dõi đơn hàng
    # Lấy danh sách khách hàng từ MongoDB
    customers = list(customers_collection.find())
    return render_template('delivery.html', locations=locations, delivery_methods=delivery_methods, customers=customers, enumerate=enumerate)

@app.route('/delivery-tracking')
def delivery_tracking():
    # Lấy thông tin đơn hàng từ cơ sở dữ liệu
    # ...

    # Hiển thị thông tin đơn hàng
    return render_template('delivery_tracking.html', delivery_status='Đang giao')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)