from flask import Blueprint, request, jsonify, g
from models import db, Product, Transaction
from auth import require_auth

products_bp = Blueprint('products', __name__)

@products_bp.route('/product', methods=['POST'])
@require_auth
def add_product():
    data = request.get_json()
    product = Product(name=data['name'], price=data['price'], description=data['description'])
    db.session.add(product)
    db.session.commit()
    return jsonify({'id': product.id, 'message': 'Product added'}), 201

@products_bp.route('/product', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description} for p in products])

@products_bp.route('/buy', methods=['POST'])
@require_auth
def buy_product():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    if not product or g.user.balance < product.price:
        return jsonify({'error': 'Insufficient balance or invalid product'}), 400
    g.user.balance -= product.price
    db.session.add(Transaction(user_id=g.user.id, kind='debit', amt=product.price, updated_bal=g.user.balance))
    db.session.commit()
    return jsonify({'message': 'Product purchased', 'balance': g.user.balance})
