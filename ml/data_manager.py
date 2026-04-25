"""
DataManager — Load, explore, and clean the banking fraud dataset.

Handles:
  • Loading the CSV from disk
  • Summary statistics and info
  • Data cleaning (duplicates, missing values)
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Optional


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATASET_FILENAME = "Bank_Transaction_Fraud_Detection.csv"
DATASET_PATH = os.path.join(DATA_DIR, DATASET_FILENAME)


class DataManager:
    """Load, explore, and clean the banking fraud dataset."""

    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = dataset_path
        self.df: Optional[pd.DataFrame] = None
        self.df_clean: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    def load_dataset(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load the dataset from CSV.

        Args:
            nrows: number of rows to load (None = all)

        Returns:
            raw DataFrame
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(
                f"Dataset not found at: {self.dataset_path}\n"
                f"Place 'Bank_Transaction_Fraud_Detection.csv' in the data/ directory."
            )

        self.df = pd.read_csv(self.dataset_path, nrows=nrows)
        print(f"[DATA] Loaded {len(self.df):,} rows x {len(self.df.columns)} columns")
        return self.df

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------
    def get_info(self) -> Dict:
        """Get summary info about the loaded dataset."""
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        df = self.df
        label_col = "Is_Fraud"

        info = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "total_missing": int(df.isnull().sum().sum()),
            "duplicates": int(df.duplicated().sum()),
            "label_column": label_col,
            "label_distribution": df[label_col].value_counts().to_dict() if label_col in df.columns else {},
        }

        # Numeric column stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            info["numeric_stats"] = df[numeric_cols].describe().to_dict()

        # Categorical column unique counts
        cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
        info["categorical_unique"] = {col: int(df[col].nunique()) for col in cat_cols}

        return info

    # ------------------------------------------------------------------
    # Clean
    # ------------------------------------------------------------------
    def clean(self) -> pd.DataFrame:
        """
        Clean the dataset:
          - Remove exact duplicates
          - Handle missing values (median for numeric, mode for categorical)

        Returns:
            cleaned DataFrame
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        df = self.df.copy()
        initial_rows = len(df)

        # Remove duplicates
        df = df.drop_duplicates()
        removed = initial_rows - len(df)
        if removed > 0:
            print(f"[CLEAN] Removed {removed:,} duplicate rows")

        # Handle missing values
        missing_total = df.isnull().sum().sum()
        if missing_total > 0:
            # Numeric: fill with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    df[col].fillna(df[col].median(), inplace=True)

            # Categorical: fill with mode
            cat_cols = df.select_dtypes(include=["object"]).columns
            for col in cat_cols:
                if df[col].isnull().any():
                    df[col].fillna(df[col].mode()[0], inplace=True)

            print(f"[CLEAN] Imputed {missing_total} missing values")
        else:
            print("[CLEAN] No missing values found")

        self.df_clean = df
        print(f"[CLEAN] Final shape: {df.shape}")
        return df

    # ------------------------------------------------------------------
    # Get cleaned data
    # ------------------------------------------------------------------
    def get_clean_data(self) -> pd.DataFrame:
        """Return the cleaned DataFrame (run clean() first)."""
        if self.df_clean is None:
            return self.clean()
        return self.df_clean
