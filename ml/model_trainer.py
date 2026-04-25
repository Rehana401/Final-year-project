"""
ModelTrainer — Train, cross-validate, and tune ML models.

Supports 4 algorithms:
  1. Logistic Regression
  2. Decision Tree
  3. Random Forest
  4. XGBoost (Gradient Boosting)
"""

import numpy as np
import pandas as pd
from typing import Dict, Callable, Optional

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.model_selection import StratifiedKFold, cross_val_score, RandomizedSearchCV


# Hyperparameter search spaces
PARAM_GRIDS = {
    "LR": {
        "C": [0.01, 0.1, 1, 10, 100],
        "solver": ["lbfgs", "liblinear"],
        "max_iter": [500, 1000],
    },
    "DT": {
        "max_depth": [5, 10, 15, 20, None],
        "min_samples_split": [2, 5, 10, 20],
        "min_samples_leaf": [1, 2, 5, 10],
        "criterion": ["gini", "entropy"],
    },
    "RF": {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [10, 15, 20, 25, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 5],
        "max_features": ["sqrt", "log2"],
    },
    "XGB": {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [3, 5, 7, 10],
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "subsample": [0.6, 0.8, 1.0],
        "colsample_bytree": [0.6, 0.8, 1.0],
        "min_child_weight": [1, 3, 5],
    },
}


class ModelTrainer:
    """Train and compare 4 ML models for fraud detection."""

    def __init__(self):
        self.models: Dict[str, object] = {}
        self.cv_results: Dict[str, dict] = {}
        self.best_model_name: str = None

    def _create_models(self) -> Dict[str, object]:
        """Initialize all 4 model instances."""
        return {
            "LR": LogisticRegression(
                max_iter=1000, random_state=42, n_jobs=-1
            ),
            "DT": DecisionTreeClassifier(
                random_state=42
            ),
            "RF": RandomForestClassifier(
                n_estimators=200, random_state=42, n_jobs=-1
            ),
            "XGB": XGBClassifier(
                n_estimators=200, random_state=42,
                use_label_encoder=False, eval_metric="logloss",
                n_jobs=-1, verbosity=0,
            ),
        }

    # ------------------------------------------------------------------
    # Train all models
    # ------------------------------------------------------------------
    def train_all(self, X_train: np.ndarray, y_train: np.ndarray,
                  k_folds: int = 5,
                  progress_callback: Optional[Callable] = None) -> Dict:
        """
        Train all 4 models with Stratified K-Fold cross-validation.

        Args:
            X_train: scaled training features
            y_train: training labels
            k_folds: number of CV folds
            progress_callback: callable(model_name, status_text)

        Returns:
            dict of trained model objects
        """
        models = self._create_models()
        skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)

        for name, model in models.items():
            if progress_callback:
                progress_callback(name, f"Training {name}...")

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train, y_train,
                cv=skf, scoring="f1", n_jobs=-1
            )

            self.cv_results[name] = {
                "cv_scores": cv_scores,
                "cv_mean": float(cv_scores.mean()),
                "cv_std": float(cv_scores.std()),
            }

            # Train on full training set
            model.fit(X_train, y_train)
            self.models[name] = model

            print(f"[TRAIN] {name}: CV F1 = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

            if progress_callback:
                progress_callback(name, f"✅ {name} trained — CV F1: {cv_scores.mean():.4f}")

        return self.models

    # ------------------------------------------------------------------
    # Get CV results
    # ------------------------------------------------------------------
    def get_cv_results(self) -> Dict:
        """Return cross-validation results for all models."""
        return self.cv_results

    # ------------------------------------------------------------------
    # Hyperparameter tuning
    # ------------------------------------------------------------------
    def tune_best(self, model_name: str,
                  X_train: np.ndarray, y_train: np.ndarray,
                  n_iter: int = 50, k_folds: int = 5) -> tuple:
        """
        Tune the best model with RandomizedSearchCV.

        Args:
            model_name: name of model to tune (LR, DT, RF, XGB)
            X_train: training features
            y_train: training labels
            n_iter: number of random search iterations
            k_folds: CV folds

        Returns:
            (tuned_model, best_params, best_score)
        """
        if model_name not in PARAM_GRIDS:
            raise ValueError(f"No parameter grid for '{model_name}'")

        base_models = self._create_models()
        base_model = base_models[model_name]

        skf = StratifiedKFold(n_splits=k_folds, shuffle=True, random_state=42)

        search = RandomizedSearchCV(
            base_model, PARAM_GRIDS[model_name],
            n_iter=n_iter, cv=skf, scoring="f1",
            n_jobs=-1, random_state=42, verbose=0,
        )

        print(f"[TUNE] Tuning {model_name} with {n_iter} iterations...")
        search.fit(X_train, y_train)

        best_model = search.best_estimator_
        best_params = search.best_params_
        best_score = search.best_score_

        print(f"[TUNE] Best params: {best_params}")
        print(f"[TUNE] Best CV F1: {best_score:.4f}")

        # Update stored model
        self.models[model_name] = best_model

        return best_model, best_params, best_score
