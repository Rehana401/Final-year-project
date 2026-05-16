from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
from extensions import db_manager

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    with db_manager._get_connection() as conn:
        row = conn.execute("SELECT userId, username, email, is_admin, createdAt, lastLogin FROM USERS WHERE userId = ?", (user_id,)).fetchone()
    
    if row:
        return jsonify({"profile": dict(row)}), 200
    return jsonify({"msg": "User not found"}), 404

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    if not username or not email:
        return jsonify({"msg": "Missing required fields"}), 400
        
    with db_manager._get_connection() as conn:
        try:
            conn.execute("UPDATE USERS SET username = ?, email = ? WHERE userId = ?", (username, email, user_id))
            return jsonify({"msg": "Profile updated"}), 200
        except Exception as e:
            return jsonify({"msg": str(e)}), 400

@user_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"msg": "Missing passwords"}), 400
        
    with db_manager._get_connection() as conn:
        row = conn.execute("SELECT password FROM USERS WHERE userId = ?", (user_id,)).fetchone()
        
    if not row:
        return jsonify({"msg": "User not found"}), 404
        
    if not bcrypt.checkpw(old_password.encode('utf-8'), row['password'].encode('utf-8')):
        return jsonify({"msg": "Incorrect old password"}), 400
        
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    with db_manager._get_connection() as conn:
        conn.execute("UPDATE USERS SET password = ? WHERE userId = ?", (hashed, user_id))
        
    return jsonify({"msg": "Password updated successfully"}), 200
