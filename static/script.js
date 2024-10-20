






function editCustomer(customer_id, name, gender, age, street, city, postal_code, phone, email, role) {
    document.getElementById('customer_id_edit').value = customer_id;
    document.getElementById('name_edit').value = name;
    document.getElementById('gender_edit').value = gender;
    document.getElementById('age_edit').value = age;
    document.getElementById('street_edit').value = street;
    document.getElementById('city_edit').value = city;
    document.getElementById('postal_code_edit').value = postal_code;
    document.getElementById('phone_edit').value = phone;
    document.getElementById('email_edit').value = email;
    document.getElementById('role_edit').value = role;
}
function editLocation(location_id, city, postal_code, address, country, contact_number, type) {
    document.getElementById('location_id_edit').value = location_id;
    document.getElementById('city_edit').value = city;
    document.getElementById('postal_code_edit').value = postal_code;
    document.getElementById('address_edit').value = address;
    document.getElementById('country_edit').value = country;
    document.getElementById('contact_number_edit').value = contact_number;
    document.getElementById('type_edit').value = type;
}
function deleteCustomer() {
    return confirmDeleteCustomer = confirm('Bạn có chắc chắn muốn xóa khách hàng này không?');
}
function editProduct(product_id, name, category, brand, price, stock, supplier_id, description) {
    document.getElementById('product_id_edit').value = product_id;
    document.getElementById('name_edit').value = name;
    document.getElementById('category_edit').value = category;
    document.getElementById('brand_edit').value = brand;
    document.getElementById('price_edit').value = price;
    document.getElementById('stock_edit').value = stock;
    document.getElementById('supplier_id_edit').value = supplier_id;
    document.getElementById('description_edit').value = description;
}
function editSupplier(supplier_id, name, phone, email, address) {
    document.getElementById('supplier_id_edit').value = supplier_id;
    document.getElementById('name_edit').value = name;
    document.getElementById('phone_edit').value = phone;
    document.getElementById('email_edit').value = email;
    document.getElementById('address_edit').value = address;

}
