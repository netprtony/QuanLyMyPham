from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from order_routes import order_bp 
from customer_routes import customer_bp
from product_routes import product_bp
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
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)
app.register_blueprint(product_bp)

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