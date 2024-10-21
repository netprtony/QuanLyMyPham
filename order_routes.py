from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
orders_collection = db['Orders']
customers_collection = db['Customers']
location_collection = db['Deliveries']
# Tạo một Blueprint cho các route của đơn hàng
order_bp = Blueprint('order_bp', __name__)




@order_bp.route('/order-list')
def order_list():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    customer_id = request.args.get('customer_id')
    total_price_str = request.args.get('total_price')
    status = request.args.get('status')  # Không có giá trị mặc định

    # Khởi tạo điều kiện truy vấn
    query_conditions = {}

    # Thêm điều kiện về thời gian nếu có
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)

            query_conditions["$expr"] = {
                "$and": [
                    { "$gte": [{ "$toDate": "$order_date" }, start_date] },
                    { "$lt": [{ "$toDate": "$order_date" }, end_date] }
                ]
            }
        except ValueError as e:
            print(f"Lỗi định dạng ngày tháng: {e}")
            return "Định dạng ngày tháng không hợp lệ", 400

    # Thêm điều kiện cho mã khách hàng nếu có
    if customer_id:
        query_conditions["customer_id"] = customer_id

    # Thêm điều kiện cho tổng giá nếu có
    if total_price_str:
        total_price = float(total_price_str)
        query_conditions["total_price"] = {"$gt": total_price}

    # Thêm điều kiện cho trạng thái nếu không chọn "Tất cả"
    if status:
        query_conditions["status"] = status

    # Thực hiện truy vấn
    orders = list(orders_collection.find(query_conditions))
    print(f"Orders Found: {orders}")

    # Lấy thông tin khách hàng
    customer_ids = [order["customer_id"] for order in orders]  # Danh sách mã khách hàng
    customers = customers_collection.find({"customer_id": {"$in": customer_ids}})

    customer_details = {customer["customer_id"]: customer["name"] for customer in customers}

    return render_template('order_list.html', orders=orders, customer_details=customer_details, enumerate=enumerate)

    
@order_bp.route('/order-detail/<order_id>')
def order_detail(order_id):
    # Tìm đơn hàng dựa trên order_id
    order = orders_collection.find_one({"order_id": order_id})
    delivery_locations = location_collection.find()
    if not order:
        return "Đơn hàng không tồn tại", 404  # Thông báo lỗi nếu không tìm thấy đơn hàng

    # Truy vấn khách hàng liên quan đến đơn hàng
    customer = customers_collection.find_one({"customer_id": order['customer_id']})

    # Gửi dữ liệu đơn hàng và thông tin khách hàng vào template
    return render_template('order_detail.html', order=order, customer=customer, delivery_locations=delivery_locations)

@order_bp.route('/update-order/<order_id>', methods=['POST'])
def update_order(order_id):
    data = request.form
    
    # Extract delivery location id
    delivery_location_id = data.get('delivery_location_id')

    # Extract product information
    products = []
    index = 1
    while True:
        product_name = data.get(f'product_name_{index}')
        if not product_name:
            break
        products.append({
            "product_name": product_name,
            "category": data.get(f'product_category_{index}'),
            "quantity": int(data.get(f'product_quantity_{index}')),
            "price": float(data.get(f'product_price_{index}'))
        })
        index += 1

    # Extract other order details
    total_price = float(data.get('total_price'))
    order_date = data.get('order_date')
    order_status = data.get('order_status')

    # Update the order in the database
    orders_collection.update_one(
        {"order_id": order_id},
        {
            "$set": {
                "delivery_location_id": delivery_location_id,
                "products_ordered": products,
                "total_price": total_price,
                "order_date": order_date,
                "status": order_status
            }
        }
    )

    @order_bp.route('/top-customers', methods=['GET'])
    def top_customers():
        # Lọc các đơn hàng có trạng thái "Delivered"
        delivered_orders = orders_collection.aggregate([
            {"$match": {"status": "Delivered"}},
            {"$group": {
                "_id": "$customer_id",
                "delivery_count": {"$sum": 1}
            }},
            {"$sort": {"delivery_count": -1}}  # Sắp xếp theo số lượng giảm dần
        ])

        # Lấy danh sách mã khách hàng từ kết quả
        customer_ids = [order["_id"] for order in delivered_orders]

        # Truy vấn chi tiết khách hàng trong collection Customers
        customers = customers_collection.find({"customer_id": {"$in": customer_ids}})

        # Ghép thông tin khách hàng và số lần nhận hàng
        customer_info = []
        for customer in customers:
            delivery_count = next(
                (o["delivery_count"] for o in delivered_orders if o["_id"] == customer["customer_id"]),
                0
            )
            if delivery_count > 0:
                customer_info.append({
                    "customer_id": customer["customer_id"],
                    "name": customer["name"],
                    "phone": customer["phone"],
                    "address": customer["address"],
                    "delivery_count": delivery_count
                })

        return render_template('top_customers.html', customer_info=customer_info)

    return redirect(url_for('order_bp.order_list'))

@order_bp.route('/orders', methods=['GET'])
def list_orders_by_status():
    # Lấy trạng thái đơn hàng từ query parameter
    order_status = request.args.get('status')
    
    # Kiểm tra nếu trạng thái có được cung cấp
    if order_status:
        # Lọc đơn hàng theo trạng thái
        orders = orders_collection.find({"status": order_status})
    else:
        # Nếu không có trạng thái được cung cấp, trả về tất cả đơn hàng
        orders = orders_collection.find()

    # Chuyển đổi kết quả thành danh sách
    orders_list = list(orders)

    return render_template('order_list.html', orders=orders_list)