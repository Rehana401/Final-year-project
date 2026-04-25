"""
HistoryManager — Business-logic layer for analysis history operations.

Wraps DatabaseManager methods and adds export functionality.
"""

import csv
import io
import json
from datetime import datetime
from typing import List


class HistoryManager:
    """Manage analysis history: save, fetch, filter, delete, export."""

    def __init__(self, db_manager):
        self.db = db_manager

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    def save_result(self, user_id: str, transaction_details: str,
                    label: str, risk_score: float,
                    confidence: float, shap_values: dict = None) -> str:
        """Save a prediction result to history. Returns historyId."""
        return self.db.save_search(
            user_id=user_id,
            transaction_details=transaction_details,
            result_label=label,
            risk_score=risk_score,
            confidence_score=confidence,
            feature_importance=shap_values,
        )

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------
    def get_user_history(self, user_id: str,
                         start_date: str = None,
                         end_date: str = None) -> List[dict]:
        """Fetch history for a user, optionally filtered by date."""
        return self.db.get_history(user_id, start_date, end_date)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete_record(self, history_id: str, user_id: str) -> bool:
        """Delete a single analysis history record."""
        return self.db.delete_history(history_id, user_id)

    # ------------------------------------------------------------------
    # Export — CSV
    # ------------------------------------------------------------------
    def export_csv(self, records: List[dict]) -> str:
        """Export a list of history records to CSV string."""
        if not records:
            return ""

        output = io.StringIO()
        fieldnames = [
            "transactionDetails", "resultLabel", "riskScore",
            "confidenceScore", "predictedAt", "exportedAs",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames,
                                extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

        # Update export status
        for rec in records:
            self.db.update_export_status(rec.get("historyId", ""), "csv")

        return output.getvalue()

    # ------------------------------------------------------------------
    # Export — PDF (delegates to report_generator)
    # ------------------------------------------------------------------
    def export_pdf(self, records: List[dict], username: str) -> bytes:
        """Export history records as a PDF report. Returns PDF bytes."""
        from core.report_generator import ReportGenerator
        gen = ReportGenerator()
        pdf_bytes = gen.generate_history_report(records, username)

        for rec in records:
            self.db.update_export_status(rec.get("historyId", ""), "pdf")

        return pdf_bytes
