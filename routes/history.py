import json
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import history_manager

history_bp = Blueprint('history', __name__)

@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    records = history_manager.get_user_history(user_id, start_date, end_date)
    return jsonify({"records": records}), 200

@history_bp.route('/', methods=['POST'])
@jwt_required()
def save_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        txn_summary = json.dumps(data.get('transaction_details', {}), default=str)
        history_id = history_manager.save_result(
            user_id=user_id,
            transaction_details=txn_summary,
            label=data.get('label'),
            risk_score=data.get('risk_score'),
            confidence=data.get('confidence'),
            shap_values=data.get('shap_values')
        )
        return jsonify({"historyId": history_id}), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@history_bp.route('/<history_id>', methods=['DELETE'])
@jwt_required()
def delete_history(history_id):
    user_id = get_jwt_identity()
    success = history_manager.delete_record(history_id, user_id)
    if success:
        return jsonify({"msg": "Deleted successfully"}), 200
    return jsonify({"msg": "Failed to delete"}), 400

@history_bp.route('/export/csv', methods=['POST'])
@jwt_required()
def export_csv():
    user_id = get_jwt_identity()
    data = request.get_json()
    records = data.get('records', [])
    
    if not records:
        return jsonify({"msg": "No records to export"}), 400
        
    csv_data = history_manager.export_csv(records)
    
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=analysis_history.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@history_bp.route('/export/pdf', methods=['POST'])
@jwt_required()
def export_pdf():
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    username = claims.get('username', 'User')
    
    data = request.get_json()
    records = data.get('records', [])
    
    if not records:
        return jsonify({"msg": "No records to export"}), 400
        
    pdf_bytes = history_manager.export_pdf(records, username)
    
    response = make_response(pdf_bytes)
    response.headers['Content-Disposition'] = 'attachment; filename=analysis_history.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    return response
