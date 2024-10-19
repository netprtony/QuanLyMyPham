from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from order_routes import order_bp 
from customer_routes import customer_bp
from product_routes import product_bp
from supplier_routes import supplier_bp
from location_routes import location_bp
client = MongoClient('mongodb://localhost:27017')
db = client['QL_CosmeticsStore']
customers_collection = db['Customers']
delivery_collection = db['Deliveries']
products_collection = db['Products']
order_collection = db['Orders']



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thiết lập secret_key cho session
# Đăng ký Blueprint cho các route của đơn hàng
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)
app.register_blueprint(product_bp)
app.register_blueprint(supplier_bp)
app.register_blueprint(location_bp)

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


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)