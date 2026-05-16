"""
FeatureExtractor — Computes derived features from raw bank transaction data.

Works with:
  • Raw dataset rows (pandas Series from the CSV)
  • Manual input from the dashboard form
  • Batch processing of DataFrames

Produces ~46 features after one-hot and frequency encoding.
"""

import re
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional


# Encoding maps for categorical features

ACCOUNT_TYPE_CATEGORIES = ["Savings", "Business", "Checking"]
TRANSACTION_TYPE_CATEGORIES = ["Transfer", "Bill Payment", "Debit", "Withdrawal", "Credit", "Education", "Shopping"]
MERCHANT_CATEGORY_CATEGORIES = ["Restaurant", "Groceries", "Entertainment", "Health", "Clothing", "Electronics"]
DEVICE_TYPE_CATEGORIES = ["POS", "Desktop", "Mobile"]
TRANSACTION_DEVICE_CATEGORIES = [
    "Self-service Banking Machine", "Wearable Device",
    "Tablet", "Desktop/Laptop", "Voice Assistant",
    "POS Mobile Device", "Banking Chatbot", "Web Browser",
    "Mobile Device", "Payment Gateway Device", "POS Mobile App", 
    "Bank Branch", "POS Terminal",
]

# Columns to drop from raw dataset
DROP_COLUMNS = [
    "Customer_ID", "Customer_Name", "Transaction_ID", "Merchant_ID",
    "Customer_Contact", "Customer_Email", "Transaction_Currency",
    "Transaction_Location", "Transaction_Description", "Gender",
    "State", "City", "Bank_Branch",
]

# Core numeric feature names (before one-hot encoding)
NUMERIC_FEATURES = [
    "Transaction_Amount", "Account_Balance", "Age",
    "Amount_to_Balance_Ratio", "Is_Night_Transaction", "Is_Weekend",
    "Hour", "DayOfWeek", "Month",
]


class FeatureExtractor:
    """Compute feature vectors from raw bank transaction data."""

    def __init__(self):
        self.frequency_maps = {}  # Fitted during training
        self.feature_columns = None  # Set after first full extraction

    # ------------------------------------------------------------------
    # Temporal feature extraction
    # ------------------------------------------------------------------
    @staticmethod
    def extract_temporal_features(date_str: str, time_str: str) -> Dict:
        """Extract temporal features from date and time strings."""
        result = {"Hour": 12, "DayOfWeek": 0, "Month": 1,
                  "Is_Weekend": 0, "Is_Night_Transaction": 0}

        # Parse time
        if time_str and isinstance(time_str, str):
            try:
                parts = time_str.strip().split(":")
                hour = int(parts[0])
                result["Hour"] = hour
                result["Is_Night_Transaction"] = 1 if 0 <= hour < 6 else 0
            except (ValueError, IndexError):
                pass

        # Parse date
        if date_str and isinstance(date_str, str):
            try:
                dt = datetime.strptime(date_str.strip(), "%d-%m-%Y")
                result["DayOfWeek"] = dt.weekday()  # 0=Mon, 6=Sun
                result["Month"] = dt.month
                result["Is_Weekend"] = 1 if dt.weekday() >= 5 else 0
            except ValueError:
                pass

        return result

    # ------------------------------------------------------------------
    # Amount-to-balance ratio
    # ------------------------------------------------------------------
    @staticmethod
    def calc_amount_to_balance_ratio(amount: float, balance: float) -> float:
        """Ratio of transaction amount to account balance. >1.0 is suspicious."""
        return amount / (balance + 1.0)

    # ------------------------------------------------------------------
    # Frequency encoding (fit on training data)
    # ------------------------------------------------------------------
    def fit_frequency_encoding(self, df: pd.DataFrame,
                               columns: List[str] = None):
        """Fit frequency encoding maps from training data."""
        if columns is None:
            columns = []

        for col in columns:
            if col in df.columns:
                freq = df[col].value_counts(normalize=True).to_dict()
                self.frequency_maps[col] = freq

    def apply_frequency_encoding(self, df: pd.DataFrame,
                                  columns: List[str] = None) -> pd.DataFrame:
        """Apply pre-fitted frequency encoding to a DataFrame."""
        if columns is None:
            columns = []

        df = df.copy()
        for col in columns:
            freq_col = f"{col}_freq"
            if col in df.columns and col in self.frequency_maps:
                freq_map = self.frequency_maps[col]
                df[freq_col] = df[col].map(freq_map).fillna(0.0)
            elif col in df.columns:
                # Fallback: use raw value counts from this DataFrame
                freq = df[col].value_counts(normalize=True).to_dict()
                df[freq_col] = df[col].map(freq).fillna(0.0)
            else:
                df[freq_col] = 0.0

        return df

    # ------------------------------------------------------------------
    # Full dataset extraction
    # ------------------------------------------------------------------
    def extract_from_dataframe(self, df: pd.DataFrame,
                                fit_frequency: bool = False) -> pd.DataFrame:
        """
        Transform raw DataFrame into engineered feature DataFrame.

        Args:
            df: raw DataFrame from CSV
            fit_frequency: if True, fit frequency maps on this data

        Returns:
            DataFrame with all engineered features (numeric + one-hot encoded)
        """
        df = df.copy()

        # --- Drop irrelevant columns ---
        cols_to_drop = [c for c in DROP_COLUMNS if c in df.columns]
        df = df.drop(columns=cols_to_drop, errors="ignore")

        # --- Temporal features ---
        temporal = df.apply(
            lambda row: self.extract_temporal_features(
                str(row.get("Transaction_Date", "")),
                str(row.get("Transaction_Time", ""))
            ),
            axis=1, result_type="expand"
        )
        df = pd.concat([df, temporal], axis=1)

        # --- Derived features ---
        df["Amount_to_Balance_Ratio"] = df.apply(
            lambda row: self.calc_amount_to_balance_ratio(
                float(row.get("Transaction_Amount", 0)),
                float(row.get("Account_Balance", 0))
            ), axis=1
        )

        # --- Drop raw date/time columns ---
        df = df.drop(columns=["Transaction_Date", "Transaction_Time"], errors="ignore")

        # --- Frequency encoding for high-cardinality cols ---
        freq_cols = []
        if fit_frequency:
            self.fit_frequency_encoding(df, freq_cols)
        df = self.apply_frequency_encoding(df, freq_cols)
        df = df.drop(columns=freq_cols, errors="ignore")

        # --- One-hot encoding for low-cardinality cols ---
        cat_cols = ["Account_Type", "Transaction_Type",
                    "Merchant_Category", "Transaction_Device", "Device_Type"]
        existing_cats = [c for c in cat_cols if c in df.columns]
        df = pd.get_dummies(df, columns=existing_cats, drop_first=True, dtype=int)

        # Store feature columns (exclude target)
        if "Is_Fraud" in df.columns:
            self.feature_columns = [c for c in df.columns if c != "Is_Fraud"]
        else:
            self.feature_columns = list(df.columns)

        return df

    # ------------------------------------------------------------------
    # Manual input extraction (for dashboard)
    # ------------------------------------------------------------------
    def extract_from_manual_input(self, transaction_amount: float,
                                   account_balance: float, age: int,
                                   account_type: str,
                                   transaction_type: str,
                                   merchant_category: str,
                                   device_type: str,
                                   transaction_device: str,
                                   hour: int, day_of_week: int) -> pd.DataFrame:
        """
        Convert manual dashboard inputs into feature DataFrame
        matching the training schema.
        """
        # Build a single-row DataFrame matching raw CSV structure
        raw_data = {
            "Transaction_Amount": [transaction_amount],
            "Account_Balance": [account_balance],
            "Age": [age],
            "Account_Type": [account_type],
            "Transaction_Type": [transaction_type],
            "Merchant_Category": [merchant_category],
            "Device_Type": [device_type],
            "Transaction_Device": [transaction_device],
            "Amount_to_Balance_Ratio": [self.calc_amount_to_balance_ratio(
                transaction_amount, account_balance
            )],
            "Hour": [hour],
            "DayOfWeek": [day_of_week],
            "Month": [1],  # default
            "Is_Weekend": [1 if day_of_week >= 5 else 0],
            "Is_Night_Transaction": [1 if 0 <= hour < 6 else 0],
        }

        df = pd.DataFrame(raw_data)

        # Frequency encoding
        df = self.apply_frequency_encoding(df, [])

        # One-hot encoding
        cat_cols = ["Account_Type", "Transaction_Type",
                    "Merchant_Category", "Transaction_Device", "Device_Type"]
        existing_cats = [c for c in cat_cols if c in df.columns]
        df = pd.get_dummies(df, columns=existing_cats, drop_first=True, dtype=int)

        # Align columns with training features
        if self.feature_columns is not None:
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0
            df = df[self.feature_columns]

        return df

    # ------------------------------------------------------------------
    # Random transaction generation (for real-time monitor)
    # ------------------------------------------------------------------
    @staticmethod
    def generate_random_transaction() -> dict:
        """Generate a random synthetic transaction for the monitoring dashboard."""
        import random

        return {
            "Transaction_Amount": round(random.uniform(10, 99000), 2),
            "Account_Balance": round(random.uniform(5000, 100000), 2),
            "Age": random.randint(18, 70),
            "Account_Type": random.choice(ACCOUNT_TYPE_CATEGORIES),
            "Transaction_Type": random.choice(TRANSACTION_TYPE_CATEGORIES),
            "Merchant_Category": random.choice(MERCHANT_CATEGORY_CATEGORIES),
            "Device_Type": random.choice(DEVICE_TYPE_CATEGORIES),
            "Transaction_Device": random.choice(TRANSACTION_DEVICE_CATEGORIES),
            "Hour": random.randint(0, 23),
            "DayOfWeek": random.randint(0, 6),
        }
