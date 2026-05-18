import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has expired"}), 401
        
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Invalid token"}), 401
        
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"msg": "Missing token"}), 401
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.predict import predict_bp
    from routes.history import history_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(predict_bp, url_prefix='/api/predict')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    @app.route('/api/stats', methods=['GET'])
    @jwt_required()
    def get_stats():
        current_user = get_jwt_identity()
        from extensions import db_manager, prediction_engine
        return jsonify({
            "users": db_manager.get_user_count(),
            "analyses": db_manager.get_user_analyses_count(current_user),
            "model_ready": prediction_engine.is_ready()
        }), 200

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
