from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'User already exists'}), 400
    hashed_password = generate_password_hash(data['password'])
    user = User(username=data['username'], hashed_password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201
