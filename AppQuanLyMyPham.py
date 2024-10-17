from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from order_routes import order_bp 

client = MongoClient('mongodb://localhost:27017')
db = client['QL_CosmeticsStore']
customers_collection = db['Customers']
delivery_collection = db['Deliveries']
products_collection = db['Products']
order_collection = db['Orders']
supplier_collection = db['Suppliers']


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thiết lập secret_key cho session
# Đăng ký Blueprint cho các route của đơn hàng
app.register_blueprint(order_bp)
# Danh sách khách hàng và địa điểm lưu trữ tạm thời
customers = []
locations = []  # Danh sách địa điểm giao hàng
products = []
delivery_methods = ['Giao hàng tiết kiệm', 'Giao hàng nhanh', 'Giao hàng tận nơi', 'Chọn địa điểm nhận hàng']
@app.route('/')
def home():
    username = session.get('username', 'Người Dùng A')  # Lấy username từ session
    return render_template('layout.html', username=username)

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

#sửa khách hàng
@app.route('/edit_customer', methods=['GET', 'POST'])
def edit_customer():
    # Lấy customer_id từ query string
    customer_id = request.args.get('id')

    # Chuyển đổi customer_id thành ObjectId nếu cần thiết (nếu sử dụng MongoDB)
    customer = customers_collection.find_one({'customer_id': customer_id})

    if request.method == 'POST':
        # Cập nhật thông tin khách hàng từ form
        customer['name'] = request.form['name']
        customer['address'] = request.form['address']
        customer['phone'] = request.form['phone']
        customer['email'] = request.form['email']

        # Cập nhật dữ liệu trong MongoDB
        customers_collection.update_one({'customer_id': customer_id}, {'$set': customer})

        return redirect(url_for('customer_list'))

    return render_template('edit_customer.html', customer=customer)





# xóa khách hàng
@app.route('/delete-customer/<string:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    # Xóa khách hàng khỏi MongoDB
    customers_collection.delete_one({'customer_id': customer_id})
    return redirect(url_for('customer_list'))


#####Products###
@app.route('/products-list')
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

        result = delivery_collection.insert_one({
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