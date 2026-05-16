import os
import joblib
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import prediction_engine, history_manager
from core.feature_extractor import FeatureExtractor
import pandas as pd

predict_bp = Blueprint('predict', __name__)

def get_extractor():
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    extractor_path = os.path.join(PROJECT_ROOT, "models", "feature_extractor.pkl")
    if os.path.exists(extractor_path):
        return joblib.load(extractor_path)
    return FeatureExtractor()

@predict_bp.route('/single', methods=['POST'])
@jwt_required()
def predict_single():
    if not prediction_engine.is_ready():
        return jsonify({"msg": "Model not loaded. Please train a model first."}), 400
        
    data = request.get_json()
    
    # Extract params from request
    amount = float(data.get('transaction_amount', 0))
    balance = float(data.get('account_balance', 0))
    age = int(data.get('age', 30))
    account_type = data.get('account_type', 'Savings')
    txn_type = data.get('transaction_type', 'Debit')
    merchant_cat = data.get('merchant_category', 'Groceries')
    device_type = data.get('device_type', 'Mobile')
    txn_device = data.get('transaction_device', 'Mobile Device')
    hour = int(data.get('hour', 12))
    day_of_week = int(data.get('day_of_week', 0))
    account_number = data.get('account_number', 'N/A')
    customer_email = data.get('customer_email', 'N/A')
    time_str = data.get('time', f'{hour}:00')
    day_name = data.get('day_name', 'N/A')

    if amount > balance:
        return jsonify({"msg": "Transaction Amount cannot be greater than Account Balance"}), 400

    extractor = get_extractor()
    features_df = extractor.extract_from_manual_input(
        transaction_amount=amount,
        account_balance=balance,
        age=age,
        account_type=account_type,
        transaction_type=txn_type,
        merchant_category=merchant_cat,
        device_type=device_type,
        transaction_device=txn_device,
        hour=hour,
        day_of_week=day_of_week,
    )

    raw_values = {
        "Account_Number": account_number,
        "Customer_Email": customer_email,
        "Transaction_Amount": amount,
        "Account_Balance": balance,
        "Age": age,
        "Account_Type": account_type,
        "Transaction_Type": txn_type,
        "Merchant_Category": merchant_cat,
        "Device_Type": device_type,
        "Transaction_Device": txn_device,
        "Hour": hour,
        "Time": time_str,
        "Day_Of_Week": day_name,
    }

    prediction = prediction_engine.predict(features_df, raw_values)
    
    # generate email alert if fraud
    alert = None
    if prediction['label'] == 'fraud':
        from core.alert_simulator import AlertSimulator
        alert = AlertSimulator.generate_alert(raw_values, prediction)
        prediction['email_alert'] = alert

    return jsonify({"prediction": prediction, "raw_values": raw_values}), 200

@predict_bp.route('/batch', methods=['POST'])
@jwt_required()
def predict_batch():
    if not prediction_engine.is_ready():
        return jsonify({"msg": "Model not loaded"}), 400
        
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
        
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({"msg": f"Failed to read CSV: {str(e)}"}), 400
        
    extractor = get_extractor()
    results = []
    
    for i, row in df.iterrows():
        try:
            features_df = extractor.extract_from_manual_input(
                transaction_amount=float(row.get("Transaction_Amount", 0)),
                account_balance=float(row.get("Account_Balance", 50000)),
                age=int(row.get("Age", 30)),
                account_type=str(row.get("Account_Type", "Savings")),
                transaction_type=str(row.get("Transaction_Type", "Debit")),
                merchant_category=str(row.get("Merchant_Category", "Groceries")),
                device_type=str(row.get("Device_Type", "Mobile")),
                transaction_device=str(row.get("Transaction_Device", "Mobile Device")),
                hour=int(row.get("Hour", 12)),
                day_of_week=int(row.get("DayOfWeek", 2)),
            )

            prediction = prediction_engine.predict(features_df)

            results.append({
                "amount": float(row.get("Transaction_Amount", 0)),
                "transaction_type": str(row.get("Transaction_Type", "N/A")),
                "label": prediction["label"],
                "confidence": prediction["confidence"],
                "risk_score": prediction["risk_score"],
                "risk_tier": prediction["risk_tier"],
            })
        except Exception as e:
            # Optionally log error, we just append error
            results.append({"error": str(e), "row": i})
            
    return jsonify({"results": results}), 200
