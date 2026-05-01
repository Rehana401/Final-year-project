"""
ReportGenerator — PDF report generation using ReportLab.

Generates professional PDF reports for:
  • Single transaction analysis
  • Batch analysis results
  • Analysis history export
  • Model performance summary
"""

import io
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# Colors
PRIMARY = colors.HexColor("#0d6efd")
DANGER = colors.HexColor("#dc3545")
SUCCESS = colors.HexColor("#198754")
WARNING = colors.HexColor("#ffc107")
DARK = colors.HexColor("#212529")
LIGHT_GREY = colors.HexColor("#f8f9fa")
BORDER_GREY = colors.HexColor("#dee2e6")


class ReportGenerator:
    """Generate professional PDF reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Add custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            "ReportTitle",
            parent=self.styles["Heading1"],
            fontSize=22,
            textColor=PRIMARY,
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            "SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=DARK,
            spaceBefore=16,
            spaceAfter=8,
            borderWidth=1,
            borderColor=PRIMARY,
            borderPadding=4,
        ))
        self.styles.add(ParagraphStyle(
            "Label_Fraud",
            parent=self.styles["Normal"],
            fontSize=16,
            textColor=DANGER,
            alignment=TA_CENTER,
            spaceAfter=8,
        ))
        self.styles.add(ParagraphStyle(
            "Label_Legit",
            parent=self.styles["Normal"],
            fontSize=16,
            textColor=SUCCESS,
            alignment=TA_CENTER,
            spaceAfter=8,
        ))
        self.styles.add(ParagraphStyle(
            "FooterStyle",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ))

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    @staticmethod
    def _add_footer(canvas, doc):
        """Draw footer on every page."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            A4[0] / 2, 0.5 * inch,
            f"Fraud Detection System  |  Page {doc.page}  |  Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        canvas.restoreState()

    # ------------------------------------------------------------------
    # Single transaction report
    # ------------------------------------------------------------------
    def generate_single_report(self, transaction: dict, prediction: dict,
                                generated_by: str = "System") -> bytes:
        """Generate a PDF for a single transaction analysis."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=1 * inch, bottomMargin=1 * inch)
        elements = []

        # Title
        elements.append(Paragraph(
            "Transaction Analysis Report", self.styles["ReportTitle"]
        ))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} by {generated_by}",
            self.styles["Normal"]
        ))
        elements.append(Spacer(1, 20))

        # Transaction details
        elements.append(Paragraph("Transaction Details", self.styles["SectionHeader"]))
        txn_data = [["Field", "Value"]]
        display_fields = [
            ("Account Number", transaction.get("Account_Number", "N/A")),
            ("Customer Email", transaction.get("Customer_Email", "N/A")),
            ("Transaction Amount", f"Rs. {transaction.get('Transaction_Amount', 0):,.2f}"),
            ("Account Balance", f"Rs. {transaction.get('Account_Balance', 0):,.2f}"),
            ("Account Type", transaction.get("Account_Type", "N/A")),
            ("Transaction Type", transaction.get("Transaction_Type", "N/A")),
            ("Merchant Category", transaction.get("Merchant_Category", "N/A")),
            ("Device Type", transaction.get("Device_Type", "N/A")),
            ("Transaction Device", transaction.get("Transaction_Device", "N/A")),
            ("Transaction Time", transaction.get("Time", f"{transaction.get('Hour', 'N/A')}:00")),
            ("Day of Week", transaction.get("Day_Of_Week", "N/A")),
            ("Customer Age", str(transaction.get("Age", "N/A"))),
        ]
        for field, value in display_fields:
            txn_data.append([field, value])

        t = Table(txn_data, colWidths=[2 * inch, 4 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # Prediction result
        elements.append(Paragraph("Prediction Result", self.styles["SectionHeader"]))
        label = prediction.get("label", "unknown")
        confidence = prediction.get("confidence", 0)
        risk_score = prediction.get("risk_score", 0)
        risk_tier = prediction.get("risk_tier", "Unknown")
        style = self.styles["Label_Fraud"] if label == "fraud" else self.styles["Label_Legit"]

        elements.append(Paragraph(
            f"<b>{label.upper()}</b>  —  Confidence: {confidence:.1%}  |  "
            f"Risk Score: {risk_score}/100 ({risk_tier})",
            style
        ))
        elements.append(Spacer(1, 16))

        # Risk flags
        risk_flags = prediction.get("risk_flags", {})
        if risk_flags:
            elements.append(Paragraph("Risk Assessment", self.styles["SectionHeader"]))
            risk_data = [["Feature", "Status", "Assessment"]]
            for fname, info in risk_flags.items():
                risk_data.append([fname, info["flag"], info["note"]])

            rt = Table(risk_data, colWidths=[2 * inch, 0.6 * inch, 3.4 * inch])
            rt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(rt)

        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        return buffer.getvalue()

    # ------------------------------------------------------------------
    # Batch report
    # ------------------------------------------------------------------
    def generate_batch_report(self, results: List[dict],
                               generated_by: str = "System") -> bytes:
        """Generate a PDF for batch analysis results."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=1 * inch, bottomMargin=1 * inch)
        elements = []

        total = len(results)
        fraud_count = sum(1 for r in results if r.get("label") == "fraud")
        legit_count = total - fraud_count

        # Cover page
        elements.append(Spacer(1, 100))
        elements.append(Paragraph("Batch Analysis Report", self.styles["ReportTitle"]))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} by {generated_by}",
            ParagraphStyle("Centered", parent=self.styles["Normal"], alignment=TA_CENTER)
        ))
        elements.append(Spacer(1, 40))

        # Summary
        summary_data = [
            ["Metric", "Value"],
            ["Total Transactions", str(total)],
            ["Fraudulent", str(fraud_count)],
            ["Legitimate", str(legit_count)],
            ["Fraud Rate", f"{fraud_count / max(total, 1) * 100:.1f}%"],
        ]
        st = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        st.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(st)
        elements.append(PageBreak())

        # Detailed results
        elements.append(Paragraph("Detailed Results", self.styles["SectionHeader"]))
        results_data = [["#", "Amount", "Type", "Label", "Risk", "Confidence"]]
        for i, r in enumerate(results[:100], 1):  # Cap at 100 rows
            results_data.append([
                str(i),
                f"Rs. {r.get('amount', 0):,.0f}",
                r.get("transaction_type", "N/A"),
                r.get("label", "N/A").upper(),
                str(r.get("risk_score", 0)),
                f"{r.get('confidence', 0):.1%}",
            ])

        rt = Table(results_data, colWidths=[0.4*inch, 1.2*inch, 1.2*inch, 1*inch, 0.8*inch, 1*inch])
        rt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (4, 0), (5, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(rt)

        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        return buffer.getvalue()

    # ------------------------------------------------------------------
    # History report
    # ------------------------------------------------------------------
    def generate_history_report(self, records: List[dict],
                                 username: str) -> bytes:
        """Generate a PDF export of analysis history records."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                topMargin=1 * inch, bottomMargin=1 * inch)
        elements = []

        elements.append(Paragraph("Analysis History Report", self.styles["ReportTitle"]))
        elements.append(Paragraph(
            f"User: {username}  |  Records: {len(records)}  |  "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            self.styles["Normal"]
        ))
        elements.append(Spacer(1, 20))

        if records:
            data = [["Label", "Risk Score", "Confidence", "Date"]]
            for r in records:
                data.append([
                    r.get("resultLabel", "N/A").upper(),
                    str(r.get("riskScore", "N/A")),
                    f"{r.get('confidenceScore', 0):.1%}",
                    str(r.get("predictedAt", "N/A"))[:19],
                ])

            t = Table(data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 2*inch])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_GREY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("No records found.", self.styles["Normal"]))

        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        return buffer.getvalue()
