from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db_manager, prediction_engine
from ml.data_manager import DataManager
from ml.preprocessor import Preprocessor
from ml.model_trainer import ModelTrainer
from ml.model_evaluator import ModelEvaluator

admin_bp = Blueprint('admin', __name__)

def admin_required():
    claims = get_jwt()
    if not claims.get('is_admin'):
        return False
    return True

# Keep training state in memory for the wizard flow
training_state = {
    "data": None,
    "models": None,
    "evaluator": None,
    "trainer": None
}

@admin_bp.before_request
def check_admin():
    # Only applies if route is not OPTIONS
    if request.method != 'OPTIONS':
        # Need to decode jwt to check claims if applying global
        # but better to check per route or write custom decorator
        pass

@admin_bp.route('/dataset/info', methods=['GET'])
@jwt_required()
def get_dataset_info():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
        
    try:
        dm = DataManager()
        dm.load_dataset()
        info = dm.get_info()
        return jsonify({"info": info}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@admin_bp.route('/train/preprocess', methods=['POST'])
@jwt_required()
def preprocess_data():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
        
    try:
        dm = DataManager()
        df = dm.load_dataset()
        df_clean = dm.clean()
        
        preprocessor = Preprocessor()
        data = preprocessor.run_full_pipeline(
            df_clean, label_col="Is_Fraud",
            test_size=0.2, apply_smote=True,
        )
        
        training_state["data"] = data
        
        return jsonify({
            "msg": "Preprocessing complete",
            "train_samples": len(data['X_train']),
            "test_samples": len(data['X_test']),
            "features": len(data['feature_names'])
        }), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@admin_bp.route('/train/train_all', methods=['POST'])
@jwt_required()
def train_all():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
        
    data = training_state.get("data")
    if not data:
        return jsonify({"msg": "No preprocessed data. Run preprocess first."}), 400
        
    try:
        trainer = ModelTrainer()
        evaluator = ModelEvaluator()
        
        models = trainer.train_all(
            data["X_train"], data["y_train"],
            k_folds=3
        )
        
        metrics_df = evaluator.evaluate_all(models, data["X_test"], data["y_test"])
        best_name, best_model, best_metrics = evaluator.select_best(models)
        
        training_state["models"] = models
        training_state["evaluator"] = evaluator
        training_state["trainer"] = trainer
        
        # Convert metrics_df to dict for json
        metrics_dict = metrics_df.to_dict('records')
        
        return jsonify({
            "msg": "Training complete",
            "metrics": metrics_dict,
            "best_model": best_name
        }), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@admin_bp.route('/train/tune', methods=['POST'])
@jwt_required()
def tune_best():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
        
    evaluator = training_state.get("evaluator")
    trainer = training_state.get("trainer")
    data = training_state.get("data")
    
    if not evaluator or not trainer or not data:
        return jsonify({"msg": "Missing training state. Train models first."}), 400
        
    try:
        best_name = evaluator.best_model_name
        tuned_model, best_params, best_score = trainer.tune_best(
            best_name, data["X_train"], data["y_train"],
            n_iter=5, k_folds=3 # Reduced for API speed
        )
        
        model_path = evaluator.save_best_model(tuned_model)
        
        from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, roc_auc_score
        y_pred = tuned_model.predict(data["X_test"])
        y_proba = tuned_model.predict_proba(data["X_test"])[:, 1]
        
        tuned_metrics = {
            "Accuracy": accuracy_score(data["y_test"], y_pred),
            "Precision": precision_score(data["y_test"], y_pred),
            "Recall": recall_score(data["y_test"], y_pred),
            "F1-Score": f1_score(data["y_test"], y_pred),
            "AUC-ROC": roc_auc_score(data["y_test"], y_proba),
        }
        
        db_manager.save_model_metadata(
            algorithm_type=best_name,
            accuracy=tuned_metrics["Accuracy"],
            precision_score=tuned_metrics["Precision"],
            recall=tuned_metrics["Recall"],
            f1_score=tuned_metrics["F1-Score"],
            auc_roc=tuned_metrics["AUC-ROC"],
            is_best=True,
            file_path=model_path,
        )
        
        # Reload prediction engine
        prediction_engine.reload()
        
        return jsonify({
            "msg": "Tuning complete and model saved",
            "tuned_metrics": tuned_metrics,
            "best_params": best_params,
            "best_model": best_name
        }), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@admin_bp.route('/models', methods=['GET'])
@jwt_required()
def get_models():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
    return jsonify({"models": db_manager.get_all_models()}), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
    
    with db_manager._get_connection() as conn:
        rows = conn.execute("SELECT userId, username, email, is_admin, createdAt, lastLogin FROM USERS").fetchall()
    return jsonify({"users": [dict(r) for r in rows]}), 200

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    if not admin_required():
        return jsonify({"msg": "Admin access required"}), 403
        
    claims = get_jwt()
    if claims.get('email') != 'rehanakousar108727@gmail.com':
        return jsonify({"msg": "Super Admin access required to delete users"}), 403
        
    try:
        with db_manager._get_connection() as conn:
            # Prevent deleting self or primary admin logic here if needed
            # First delete associated history to prevent foreign key constraint failures
            conn.execute("DELETE FROM ANALYSIS_HISTORY WHERE userId = ?", (user_id,))
            cursor = conn.execute("DELETE FROM USERS WHERE userId = ?", (user_id,))
            
        if cursor.rowcount > 0:
            return jsonify({"msg": "User deleted successfully"}), 200
        else:
            return jsonify({"msg": "User not found"}), 404
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
