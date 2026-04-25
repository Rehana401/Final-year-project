"""
Preprocessor — Feature engineering, normalization, encoding, SMOTE.

Runs the full preprocessing pipeline:
  1. Feature engineering (temporal, ratios, encoding)
  2. Train/test split (stratified 80/20)
  3. StandardScaler normalization
  4. SMOTE oversampling (training set only)
"""

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

from core.feature_extractor import FeatureExtractor

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")
EXTRACTOR_PATH = os.path.join(MODELS_DIR, "feature_extractor.pkl")


class Preprocessor:
    """Feature engineering, scaling, encoding, and SMOTE."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_extractor = FeatureExtractor()

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------
    def engineer_features(self, df: pd.DataFrame,
                          label_col: str = "Is_Fraud",
                          fit_frequency: bool = False) -> tuple:
        """
        Run feature engineering on raw DataFrame.

        Args:
            df: cleaned DataFrame with raw columns
            label_col: target column name
            fit_frequency: if True, fit frequency encoding on this data

        Returns:
            (X: DataFrame, y: Series)
        """
        # Extract target before transforming
        y = df[label_col].astype(int).copy() if label_col in df.columns else None

        # Engineer features
        df_features = self.feature_extractor.extract_from_dataframe(
            df, fit_frequency=fit_frequency
        )

        # Separate features and target
        if label_col in df_features.columns:
            X = df_features.drop(columns=[label_col])
        else:
            X = df_features

        if y is None:
            y = pd.Series([0] * len(X))

        # Reset indices
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True)

        feature_names = list(X.columns)
        print(f"[FEATURES] Engineered {len(feature_names)} features from {len(df)} samples")

        return X, y

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------
    def normalize(self, X_train: pd.DataFrame,
                  X_test: pd.DataFrame) -> tuple:
        """
        Fit StandardScaler on X_train, transform both.
        Saves the fitted scaler to models/scaler.pkl.

        Returns:
            (X_train_scaled, X_test_scaled, scaler)
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Save scaler
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.scaler, SCALER_PATH)
        print(f"[SAVED] Scaler saved to {SCALER_PATH}")

        return X_train_scaled, X_test_scaled, self.scaler

    # ------------------------------------------------------------------
    # Label encoding
    # ------------------------------------------------------------------
    @staticmethod
    def encode_labels(y: pd.Series) -> pd.Series:
        """Ensure labels are binary integers (0/1)."""
        y = y.astype(int)
        unique = sorted(y.unique())
        print(f"[LABELS] Labels: {unique}, counts: {y.value_counts().to_dict()}")
        return y

    # ------------------------------------------------------------------
    # SMOTE
    # ------------------------------------------------------------------
    @staticmethod
    def apply_smote(X_train: np.ndarray,
                    y_train: pd.Series,
                    random_state: int = 42) -> tuple:
        """
        Apply SMOTE to balance the training set.

        Returns:
            (X_resampled, y_resampled)
        """
        print(f"[SMOTE] Before SMOTE: {pd.Series(y_train).value_counts().to_dict()}")

        smote = SMOTE(random_state=random_state)
        X_res, y_res = smote.fit_resample(X_train, y_train)

        print(f"[SMOTE] After  SMOTE: {pd.Series(y_res).value_counts().to_dict()}")
        return X_res, y_res

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------
    def run_full_pipeline(self, df: pd.DataFrame,
                          label_col: str = "Is_Fraud",
                          test_size: float = 0.2,
                          apply_smote: bool = True) -> dict:
        """
        Run the complete preprocessing pipeline:
          1. Engineer features
          2. Encode labels
          3. Train/test split (stratified)
          4. Normalize (save scaler)
          5. Apply SMOTE (optional, train only)

        Returns:
            dict with X_train, X_test, y_train, y_test, scaler, feature_names
        """
        # 1. Engineer features (fit frequency encoding on full data first)
        X, y = self.engineer_features(df, label_col, fit_frequency=True)

        # 2. Encode labels
        y = self.encode_labels(y)

        # 3. Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        print(f"[SPLIT] train={len(X_train)}, test={len(X_test)}")

        # 4. Normalize (saves scaler)
        X_train_scaled, X_test_scaled, scaler = self.normalize(X_train, X_test)

        # Save feature extractor (for prediction engine)
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.feature_extractor, EXTRACTOR_PATH)
        print(f"[SAVED] Feature extractor saved to {EXTRACTOR_PATH}")

        # 5. SMOTE
        if apply_smote:
            X_train_scaled, y_train = self.apply_smote(X_train_scaled, y_train)

        return {
            "X_train": X_train_scaled,
            "X_test": X_test_scaled,
            "y_train": np.array(y_train),
            "y_test": np.array(y_test),
            "scaler": scaler,
            "feature_names": list(X.columns),
            "X_train_df": X_train,
            "X_test_df": X_test,
            "feature_extractor": self.feature_extractor,
        }
