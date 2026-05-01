"""
AlertSimulator — Email alert simulation for flagged transactions.

Generates formatted security email alerts when a transaction
is predicted as fraudulent. Displays in the Streamlit UI.
"""

from datetime import datetime
from typing import Dict


class AlertSimulator:
    """Simulate email alerts for high-risk transactions."""

    @staticmethod
    def generate_alert(transaction: dict, prediction: dict) -> str:
        """
        Generate a formatted email alert for a fraudulent transaction.

        Args:
            transaction: raw transaction details dict
            prediction: prediction result from PredictionEngine

        Returns:
            Formatted alert string for display
        """
        risk_score = prediction.get("risk_score", 0)
        risk_tier = prediction.get("risk_tier", "Unknown")
        confidence = prediction.get("confidence", 0)

        amount = transaction.get("Transaction_Amount", 0)
        txn_type = transaction.get("Transaction_Type", "Unknown")
        device = transaction.get("Device_Type", "Unknown")
        category = transaction.get("Merchant_Category", "Unknown")
        hour = transaction.get("Hour", 0)
        age = transaction.get("Age", 0)
        account_number = transaction.get("Account_Number", "N/A")
        customer_email = transaction.get("Customer_Email", "N/A")

        # Time display
        if "Time" in transaction:
            time_str = transaction["Time"]
        else:
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            time_str = f"{display_hour}:00 {am_pm}"

        # Build risk factors
        risk_factors = []
        if 0 <= hour < 6:
            risk_factors.append(f"Night transaction ({time_str})")
        if amount > 80000:
            risk_factors.append(f"Very high amount (Rs. {amount:,.2f})")
        elif amount > 50000:
            risk_factors.append(f"High amount (Rs. {amount:,.2f})")

        balance = transaction.get("Account_Balance", 1)
        ratio = amount / (balance + 1)
        if ratio > 1.0:
            risk_factors.append(f"Amount-to-balance ratio: {ratio:.2f} (overdraft level)")
        elif ratio > 0.7:
            risk_factors.append(f"Amount-to-balance ratio: {ratio:.2f} (high)")

        if device == "Desktop" and 0 <= hour < 6:
            risk_factors.append("Desktop device during non-business hours")
        if txn_type == "Transfer":
            risk_factors.append("Transfer type — highest fraud category")

        if not risk_factors:
            risk_factors.append("Multiple risk indicators triggered")

        # Build recommended actions based on severity
        if risk_tier == "Critical":
            actions = [
                "BLOCK transaction immediately",
                "Contact account holder for 2FA verification",
                "Escalate to fraud investigation team",
                "Log incident in compliance system",
            ]
        elif risk_tier == "High":
            actions = [
                "Hold transaction for manual review",
                "Send SMS verification to account holder",
                "Flag account for enhanced monitoring",
            ]
        else:
            actions = [
                "Flag transaction for review",
                "Monitor account activity for next 24 hours",
            ]

        # Build the alert
        txn_id = f"TXN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        risk_factors_str = "\n".join(f"  ⚠️ {rf}" for rf in risk_factors)
        actions_str = "\n".join(f"  → {a}" for a in actions)

        alert = f"""📧 FRAUD ALERT — SecurBank Security System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From:    fraud-detection@securbank.com
To:      security-team@securbank.com
Subject: 🚨 {risk_tier.upper()}-RISK Transaction Detected — {txn_id}

Account Information:
  Account No:  {account_number}
  Email:       {customer_email}
  Customer:    Age {age}

Transaction Details:
  Amount:    Rs. {amount:,.2f}
  Type:      {txn_type}
  Device:    {device}
  Time:      {time_str}
  Category:  {category}

Risk Assessment:
  Risk Score:  {risk_score}/100 ({risk_tier})
  Confidence:  {confidence:.1%}

Top Risk Factors:
{risk_factors_str}

Recommended Action:
{actions_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alert generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        return alert

    @staticmethod
    def get_alert_severity_color(risk_tier: str) -> str:
        """Get the color for the risk tier badge."""
        return {
            "Critical": "#dc3545",
            "High": "#fd7e14",
            "Medium": "#ffc107",
            "Low": "#198754",
        }.get(risk_tier, "#6c757d")
