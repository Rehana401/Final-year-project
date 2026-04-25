"""
ModelEvaluator — Evaluate, compare, and select the best ML model.

Generates metrics tables, confusion matrices, ROC curves, and saves the best model.
"""

import os
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix,
)
from typing import Dict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")


class ModelEvaluator:
    """Evaluate all trained models and select the best one."""

    def __init__(self):
        self.metrics: Dict[str, dict] = {}
        self.best_model_name: str = None
        self.best_model = None

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate_all(self, models: Dict[str, object],
                     X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
        """Compute evaluation metrics for all models."""
        rows = []
        for name, model in models.items():
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            m = {
                "Model": name,
                "Accuracy": accuracy_score(y_test, y_pred),
                "Precision": precision_score(y_test, y_pred, zero_division=0),
                "Recall": recall_score(y_test, y_pred, zero_division=0),
                "F1-Score": f1_score(y_test, y_pred, zero_division=0),
                "AUC-ROC": roc_auc_score(y_test, y_proba),
            }
            self.metrics[name] = m
            rows.append(m)
            print(f"[EVAL] {name}: F1={m['F1-Score']:.4f}, AUC={m['AUC-ROC']:.4f}")

        df = pd.DataFrame(rows).sort_values("F1-Score", ascending=False)
        return df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Best model selection
    # ------------------------------------------------------------------
    def select_best(self, models: Dict[str, object],
                    metric: str = "F1-Score") -> tuple:
        """Select the best model based on F1-Score."""
        if not self.metrics:
            raise ValueError("Run evaluate_all() first.")

        best_name = max(self.metrics, key=lambda k: self.metrics[k].get(metric, 0))
        self.best_model_name = best_name
        self.best_model = models[best_name]

        print(f"\n[BEST] Best model: {best_name} ({metric}={self.metrics[best_name][metric]:.4f})")
        return best_name, self.best_model, self.metrics[best_name]

    # ------------------------------------------------------------------
    # Save best model
    # ------------------------------------------------------------------
    def save_best_model(self, model=None, path: str = MODEL_PATH) -> str:
        """Save the best model to disk."""
        if model is None:
            model = self.best_model
        if model is None:
            raise ValueError("No best model selected.")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)
        print(f"[SAVED] Best model saved to {path}")
        return path

    # ------------------------------------------------------------------
    # Confusion matrices (2×2 grid)
    # ------------------------------------------------------------------
    def plot_confusion_matrices(self, models: Dict[str, object],
                                 X_test: np.ndarray,
                                 y_test: np.ndarray) -> plt.Figure:
        """Plot 2×2 grid of confusion matrices."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        model_names = list(models.keys())[:4]
        for i, name in enumerate(model_names):
            model = models[name]
            y_pred = model.predict(X_test)
            cm = confusion_matrix(y_test, y_pred)

            sns.heatmap(
                cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Legitimate", "Fraud"],
                yticklabels=["Legitimate", "Fraud"],
                ax=axes[i],
                cbar_kws={"shrink": 0.8},
            )
            axes[i].set_title(f"{name}", fontsize=14, fontweight="bold")
            axes[i].set_xlabel("Predicted", fontsize=11)
            axes[i].set_ylabel("Actual", fontsize=11)

        plt.suptitle("Confusion Matrices", fontsize=16, fontweight="bold", y=1.02)
        plt.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # ROC curves
    # ------------------------------------------------------------------
    def plot_roc_curves(self, models: Dict[str, object],
                        X_test: np.ndarray,
                        y_test: np.ndarray) -> go.Figure:
        """Plot all ROC curves overlaid on a single Plotly chart."""
        fig = go.Figure()

        colors_map = {
            "LR": "#2ca02c",
            "DT": "#ff7f0e",
            "RF": "#1f77b4",
            "XGB": "#d62728",
        }

        for name, model in models.items():
            y_proba = model.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            auc = roc_auc_score(y_test, y_proba)

            fig.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines",
                name=f"{name} (AUC = {auc:.4f})",
                line=dict(color=colors_map.get(name, "#333"), width=2),
            ))

        # Diagonal
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines",
            name="Random (AUC = 0.5)",
            line=dict(color="gray", width=1, dash="dash"),
        ))

        fig.update_layout(
            title="ROC Curves — Model Comparison",
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            template="plotly_white",
            legend=dict(x=0.6, y=0.1),
            width=700, height=500,
        )
        return fig

    # ------------------------------------------------------------------
    # Feature importance
    # ------------------------------------------------------------------
    @staticmethod
    def plot_feature_importance(model, feature_names: list,
                                 title: str = "Feature Importance",
                                 top_n: int = 20) -> go.Figure:
        """Plot horizontal bar chart of feature importances."""
        importances = model.feature_importances_
        indices = np.argsort(importances)

        # Show top N features
        if top_n and len(indices) > top_n:
            indices = indices[-top_n:]

        fig = go.Figure(go.Bar(
            x=importances[indices],
            y=[feature_names[i] for i in indices],
            orientation="h",
            marker_color="#0d6efd",
        ))
        fig.update_layout(
            title=title,
            xaxis_title="Importance",
            yaxis_title="Feature",
            template="plotly_white",
            height=max(400, len(indices) * 22),
        )
        return fig
