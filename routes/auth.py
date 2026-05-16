from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db_manager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing email or password"}), 400
        
    user = db_manager.authenticate(data['email'].strip(), data['password'])
    if user:
        access_token = create_access_token(identity=user['userId'], additional_claims={
            "is_admin": user['is_admin'],
            "username": user['username'],
            "email": user['email']
        })
        return jsonify({"access_token": access_token, "user": user}), 200
        
    return jsonify({"msg": "Invalid email or password"}), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({"msg": "Missing required fields"}), 400
        
    if db_manager.user_exists(username=username):
        return jsonify({"msg": "Username already taken"}), 409
        
    if db_manager.user_exists(email=email):
        return jsonify({"msg": "Email already registered"}), 409
        
    try:
        user = db_manager.create_user(username, email, password)
        return jsonify({"msg": "Account created successfully", "user": user}), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    # In a real app we'd fetch full details, but for now we can just return success
    return jsonify({"userId": current_user_id}), 200
