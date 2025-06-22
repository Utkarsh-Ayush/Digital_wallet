from flask import Blueprint, request, jsonify, g
from models import db, User, Transaction
from auth import require_auth
import requests

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/fund', methods=['POST'])
@require_auth
def fund():
    data = request.get_json()
    amt = data.get('amt')
    if not amt or amt <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    g.user.balance += amt
    db.session.add(Transaction(user_id=g.user.id, kind='credit', amt=amt, updated_bal=g.user.balance))
    db.session.commit()
    return jsonify({'balance': g.user.balance})

@wallet_bp.route('/pay', methods=['POST'])
@require_auth
def pay():
    data = request.get_json()
    receiver = User.query.filter_by(username=data.get('to')).first()
    amt = data.get('amt')
    if not receiver or receiver.id == g.user.id:
        return jsonify({'error': 'Invalid recipient'}), 400
    if not amt or amt <= 0 or g.user.balance < amt:
        return jsonify({'error': 'Insufficient funds'}), 400
    g.user.balance -= amt
    receiver.balance += amt
    db.session.add(Transaction(user_id=g.user.id, kind='debit', amt=amt, updated_bal=g.user.balance))
    db.session.add(Transaction(user_id=receiver.id, kind='credit', amt=amt, updated_bal=receiver.balance))
    db.session.commit()
    return jsonify({'balance': g.user.balance})

@wallet_bp.route('/bal', methods=['GET'])
@require_auth
def balance():
    currency = request.args.get('currency', 'INR')
    amount = g.user.balance
    if currency != 'INR':
        try:
            res = requests.get(f'https://api.currencyapi.com/v3/latest?apikey=YOUR_API_KEY&base_currency=INR')
            rate = res.json()['data'][currency]['value']
            amount *= rate
        except:
            return jsonify({'error': 'Currency conversion failed'}), 500
    return jsonify({'balance': round(amount, 2), 'currency': currency})

@wallet_bp.route('/stmt', methods=['GET'])
@require_auth
def statement():
    transactions = Transaction.query.filter_by(user_id=g.user.id).order_by(Transaction.timestamp.desc()).all()
    return jsonify([
        {'kind': t.kind, 'amt': t.amt, 'updated_bal': t.updated_bal, 'timestamp': t.timestamp.isoformat()}
        for t in transactions
    ])
