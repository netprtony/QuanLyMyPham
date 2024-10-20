from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['QL_CosmeticsStore']
orders_collection = db['Orders']
customers_collection = db['Customers']
location_collection = db['Deliveries']
# Tạo một Blueprint cho các route của đơn hàng
order_bp = Blueprint('order_bp', __name__)




@order_bp.route('/order-list')
def order_list():
    orders = orders_collection.find()
    return render_template('order_list.html', orders=orders, enumerate=enumerate)
    
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

    return redirect(url_for('order_bp.order_list'))