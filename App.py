from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import os
import subprocess
from bson.objectid import ObjectId
from order_routes import order_bp 
from customer_routes import customer_bp
from product_routes import product_bp
from supplier_routes import supplier_bp
from location_routes import location_bp
from delivery_routes import delivery_bp
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
app.register_blueprint(delivery_bp)
# Danh sách khách hàng và địa điểm lưu trữ tạm thời
customers = []
locations = []  # Danh sách địa điểm giao hàng
products = []
delivery_methods = ['Giao hàng tiết kiệm', 'Giao hàng nhanh', 'Giao hàng tận nơi', 'Chọn địa điểm nhận hàng']

# Kiểm tra xem người dùng đã đăng nhập chưa
def is_logged_in():
    return 'username' in session

@app.route('/')
def home():
    if not is_logged_in():
        return redirect(url_for('login'))  # Nếu chưa đăng nhập, chuyển hướng đến trang đăng nhập
    username = session.get('username', 'admin')  # Lấy username từ session
    return render_template('layout.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra thông tin đăng nhập (nên sử dụng cơ sở dữ liệu)
        if username == 'admin' and password == '123':  # Ví dụ đơn giản
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Sai tên đăng nhập hoặc mật khẩu')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Xóa username khỏi session
    return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập


@app.route('/backup-restore', methods=['GET', 'POST'])
def backup_restore():
    if request.method == 'POST':
        if 'action' in request.form:
            action = request.form['action']
            if action == 'backup':
                return backup_data()
            elif action == 'restore':
                return restore_data(request)
    return render_template('backup_restore.html')


def backup_data():
    backup_dir = 'D:\\Backups\\'
    os.makedirs(backup_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại
    backup_file = os.path.join(backup_dir, 'QL_CosmeticsStore.bak')

    try:
        command = f"mongodump --db QL_CosmeticsStore --out {backup_dir}"  # Lệnh sao lưu
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Backup completed successfully: {backup_file}")
        return jsonify({"message": "Backup successful!", "file": backup_file}), 200
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        return jsonify({"message": "Backup failed!", "error": str(e)}), 500


def restore_data(request):
    if 'backup_file' not in request.files:
        return jsonify({"message": "No backup file provided!"}), 400

    backup_file = request.files['backup_file']  # Lấy tệp từ form
    if backup_file.filename == '':
        return jsonify({"message": "No backup file selected!"}), 400

    # Lưu tệp vào thư mục tạm thời
    temp_path = os.path.join('D:\\Backups\\', backup_file.filename)
    backup_file.save(temp_path)

    try:
        command = f"mongorestore --db QL_CosmeticsStore {temp_path}"  # Lệnh phục hồi
        subprocess.run(command, shell=True, check=True)
        logging.info("Restore completed successfully.")
        return jsonify({"message": "Restore successful!"}), 200
    except Exception as e:
        logging.error(f"Restore failed: {e}")
        return jsonify({"message": "Restore failed!", "error": str(e)}), 500

@app.route('/favorite-products')
def favorite_products():
    # Truy vấn lấy thông tin sản phẩm khách hàng ưa thích
    pipeline = [
        {
            "$unwind": "$products_ordered"  # Phân tách từng sản phẩm trong mảng products_ordered
        },
        {
            "$group": {
                "_id": {
                    "customer_id": "$customer_id",
                    "product_name": "$products_ordered.product_name",
                },
                "total_quantity": {"$sum": "$products_ordered.quantity"},  # Tính tổng số lượng của từng sản phẩm
            }
        },
        {
            "$match": {
                "total_quantity": {"$gt": 2}  # Chỉ lấy các sản phẩm có tổng số lượng lớn hơn 2
            }
        }
    ]

    results = order_collection.aggregate(pipeline)  # Thực hiện truy vấn với aggregation pipeline
    favorite_products = []

    for result in results:
        # Lấy thông tin khách hàng dựa trên customer_id
        customer = customers_collection.find_one({"customer_id": result["_id"]["customer_id"]})
        if customer:
            favorite_products.append({
                "customer_id": customer["customer_id"],
                "customer_name": customer["name"],
                "product_name": result["_id"]["product_name"],
                "total_quantity": result["total_quantity"]
            })

    return render_template('favorite_products.html', favorite_products=favorite_products)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)