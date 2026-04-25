"""
PredictionEngine — Load trained model and make fraud predictions.

Provides:
  • Model + scaler loading
  • Fraud prediction with confidence scoring
  • SHAP-based feature importance
  • Risk tier assessment
  • Per-feature risk flag generation
"""

import os
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")


class PredictionEngine:
    """Load model and scaler, predict fraud, explain results."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.explainer = None
        self._load_model()

    def _load_model(self):
        """Load the best model and scaler from disk."""
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                print(f"[ENGINE] Model loaded from {MODEL_PATH}")
            else:
                print(f"[ENGINE] No model found at {MODEL_PATH}")

            if os.path.exists(SCALER_PATH):
                self.scaler = joblib.load(SCALER_PATH)
                print(f"[ENGINE] Scaler loaded from {SCALER_PATH}")
            else:
                print(f"[ENGINE] No scaler found at {SCALER_PATH}")

        except Exception as e:
            print(f"[ENGINE] Error loading model: {e}")
            self.model = None
            self.scaler = None

    def reload(self):
        """Force reload model and scaler."""
        self.explainer = None
        self._load_model()

    def is_ready(self) -> bool:
        """Check if model and scaler are loaded."""
        return self.model is not None and self.scaler is not None

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def predict(self, features: pd.DataFrame,
                raw_values: dict = None) -> Dict:
        """
        Predict fraud for a single transaction.

        Args:
            features: DataFrame (1 row) with engineered features
            raw_values: dict of original input values (for risk flags)

        Returns:
            dict with label, confidence, risk_score, risk_tier,
            shap_values, risk_flags, low_confidence
        """
        if not self.is_ready():
            return {
                "label": "unknown", "confidence": 0.0,
                "risk_score": 0, "risk_tier": "Unknown",
                "shap_values": {}, "risk_flags": {},
                "low_confidence": True,
            }

        # Scale features
        X = features.values if isinstance(features, pd.DataFrame) else np.array(features)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        X_scaled = self.scaler.transform(X)

        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]

        label = "fraud" if prediction == 1 else "legitimate"
        confidence = float(probabilities[1]) if prediction == 1 else float(probabilities[0])
        fraud_probability = float(probabilities[1])

        # Risk score (0-100)
        risk_score = int(fraud_probability * 100)
        risk_tier = self._get_risk_tier(risk_score)

        # Low confidence flag
        low_confidence = confidence < 0.65

        # SHAP values
        shap_values = self._get_shap_values(X_scaled, features)

        # Risk flags
        risk_flags = self._assess_risk(raw_values) if raw_values else {}

        return {
            "label": label,
            "confidence": confidence,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "fraud_probability": fraud_probability,
            "shap_values": shap_values,
            "risk_flags": risk_flags,
            "low_confidence": low_confidence,
        }

    # ------------------------------------------------------------------
    # Risk tier
    # ------------------------------------------------------------------
    @staticmethod
    def _get_risk_tier(risk_score: int) -> str:
        """Map risk score to a named tier."""
        if risk_score < 25:
            return "Low"
        elif risk_score < 50:
            return "Medium"
        elif risk_score < 75:
            return "High"
        else:
            return "Critical"

    # ------------------------------------------------------------------
    # SHAP explainability
    # ------------------------------------------------------------------
    def _get_shap_values(self, X_scaled: np.ndarray,
                         features: pd.DataFrame) -> Dict:
        """Get SHAP feature importance values."""
        try:
            import shap

            if self.explainer is None:
                model_type = type(self.model).__name__
                if model_type in ("RandomForestClassifier", "XGBClassifier",
                                  "DecisionTreeClassifier", "GradientBoostingClassifier"):
                    self.explainer = shap.TreeExplainer(self.model)
                else:
                    # KernelExplainer fallback (slower)
                    background = shap.sample(X_scaled, min(50, len(X_scaled)))
                    self.explainer = shap.KernelExplainer(
                        self.model.predict_proba, background
                    )

            sv = self.explainer.shap_values(X_scaled)

            # Handle different SHAP output formats
            if isinstance(sv, list):
                sv = sv[1]  # Class 1 (fraud)
            if sv.ndim > 1:
                sv = sv[0]

            # Map to feature names
            if isinstance(features, pd.DataFrame):
                feature_names = list(features.columns)
            else:
                feature_names = [f"feature_{i}" for i in range(len(sv))]

            return {name: float(val) for name, val in zip(feature_names, sv)}

        except Exception as e:
            print(f"[ENGINE] SHAP failed: {e}")
            return {}

    # ------------------------------------------------------------------
    # Risk flag assessment
    # ------------------------------------------------------------------
    @staticmethod
    def _assess_risk(raw_values: dict) -> Dict:
        """Generate per-feature risk flags based on raw input values."""
        flags = {}

        # Amount risk
        amount = raw_values.get("Transaction_Amount", 0)
        if amount > 80000:
            flags["Transaction Amount"] = {"flag": "⚠️", "note": f"Very high amount (₹{amount:,.2f})"}
        elif amount > 50000:
            flags["Transaction Amount"] = {"flag": "⚠️", "note": f"High amount (₹{amount:,.2f})"}
        else:
            flags["Transaction Amount"] = {"flag": "✅", "note": f"Normal amount (₹{amount:,.2f})"}

        # Balance ratio
        balance = raw_values.get("Account_Balance", 1)
        ratio = amount / (balance + 1)
        if ratio > 1.0:
            flags["Amount/Balance Ratio"] = {"flag": "⚠️", "note": f"Overdraft level ({ratio:.2f})"}
        elif ratio > 0.7:
            flags["Amount/Balance Ratio"] = {"flag": "⚠️", "note": f"High ratio ({ratio:.2f})"}
        else:
            flags["Amount/Balance Ratio"] = {"flag": "✅", "note": f"Normal ratio ({ratio:.2f})"}

        # Night transaction
        hour = raw_values.get("Hour", 12)
        if 0 <= hour < 6:
            flags["Time of Day"] = {"flag": "⚠️", "note": f"Night transaction ({hour}:00 AM)"}
        elif 22 <= hour <= 23:
            flags["Time of Day"] = {"flag": "⚠️", "note": f"Late night ({hour}:00)"}
        else:
            flags["Time of Day"] = {"flag": "✅", "note": f"Normal hours ({hour}:00)"}

        # Device type
        device = raw_values.get("Device_Type", "")
        if device == "Desktop" and (0 <= hour < 6):
            flags["Device"] = {"flag": "⚠️", "note": f"Desktop at night — unusual"}
        else:
            flags["Device"] = {"flag": "✅", "note": f"Device: {device}"}

        # Transaction type
        txn_type = raw_values.get("Transaction_Type", "")
        if txn_type == "Transfer":
            flags["Transaction Type"] = {"flag": "⚠️", "note": "Transfers have highest fraud rate"}
        else:
            flags["Transaction Type"] = {"flag": "✅", "note": f"Type: {txn_type}"}

        # Age
        age = raw_values.get("Age", 30)
        flags["Customer Age"] = {"flag": "✅", "note": f"Age: {age}"}

        return flags
