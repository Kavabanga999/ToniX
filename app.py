from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy.exc import IntegrityError
from urllib.parse import quote as url_quote

app = Flask(__name__)

# Настройка базы данных
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'mining_bot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    wallet_address = db.Column(db.String(120), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    mining_speed = db.Column(db.Float, default=0.0)
    is_mining = db.Column(db.Boolean, default=False)
    last_mining_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.amount} for user {self.user_id}>'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], wallet_address=data['wallet_address'])
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({"id": new_user.id, "username": new_user.username, "wallet_address": new_user.wallet_address, "balance": new_user.balance, "mining_speed": new_user.mining_speed}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Wallet address already exists"}), 400

@app.route('/api/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    user = User.query.filter_by(wallet_address=data['wallet_address']).first()
    if user:
        new_transaction = Transaction(user_id=user.id, amount=data['amount'])
        user.balance += data['amount']
        user.mining_speed += data['amount'] * 0.01
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"message": "Deposit successful", "new_balance": user.balance, "new_mining_speed": user.mining_speed}), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/api/start_mining', methods=['POST'])
def start_mining():
    data = request.get_json()
    user = User.query.filter_by(wallet_address=data['wallet_address']).first()
    if user and not user.is_mining:
        user.is_mining = True
        user.last_mining_time = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Mining started", "mining_speed": user.mining_speed}), 200
    return jsonify({"message": "User not found or already mining"}), 404

@app.route('/api/stop_mining', methods=['POST'])
def stop_mining():
    data = request.get_json()
    user = User.query.filter_by(wallet_address=data['wallet_address']).first()
    if user and user.is_mining:
        user.is_mining = False
        db.session.commit()
        return jsonify({"message": "Mining stopped"}), 200
    return jsonify({"message": "User not found or not mining"}), 404

@app.route('/api/status', methods=['GET'])
def status():
    wallet_address = request.args.get('wallet_address')
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if user:
        return jsonify({
            "username": user.username,
            "balance": user.balance,
            "mining_speed": user.mining_speed,
            "is_mining": user.is_mining
        }), 200
    return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)