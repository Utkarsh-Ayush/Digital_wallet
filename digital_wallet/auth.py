from flask import request, jsonify, g
from functools import wraps
from models import User
from werkzeug.security import check_password_hash
from models import db

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.filter_by(username=auth.username).first()
        if not user or not check_password_hash(user.hashed_password, auth.password):
            return jsonify({'error': 'Invalid credentials'}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated
