"""
batch.py — Batch Transaction Analysis page.

Upload a CSV of transactions and analyze them all at once.
"""

from datetime import datetime

import streamlit as st
import pandas as pd

from core.feature_extractor import FeatureExtractor
from core.prediction_engine import PredictionEngine
from core.history_manager import HistoryManager
from core.report_generator import ReportGenerator


def show_batch_page(db, prediction_engine: PredictionEngine,
                    history_manager: HistoryManager):
    """Render the batch analysis page."""
    st.markdown("## 📦 Batch Transaction Analysis")
    st.markdown("Upload a CSV file with transaction data to analyze multiple transactions at once.")

    if not prediction_engine.is_ready():
        st.warning("⚠️ Model not loaded. Train the model first via Admin → Model Training.")
        st.stop()

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        help="CSV must contain columns: Transaction_Amount, Account_Balance, Age, etc.",
        key="batch_csv_upload",
    )

    if uploaded_file is None:
        st.info("📎 Upload a CSV file to get started.")
        with st.expander("📋 Required CSV columns"):
            st.code(
                "Transaction_Amount,Account_Balance,Age,Account_Type,"
                "Transaction_Type,Merchant_Category,Device_Type",
                language="csv"
            )
        return

    # Parse CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return

    st.success(f"✅ Loaded **{len(df)}** transactions from CSV.")
    st.dataframe(df.head(), use_container_width=True)

    # Run analysis
    if st.button("🚀 Start Batch Analysis", type="primary", key="start_batch_btn"):
        import os, joblib
        extractor_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models", "feature_extractor.pkl"
        )
        if os.path.exists(extractor_path):
            extractor = joblib.load(extractor_path)
        else:
            extractor = FeatureExtractor()

        results = []
        errors = []
        progress_bar = st.progress(0, text="Starting batch analysis...")

        for i, (_, row) in enumerate(df.iterrows()):
            progress = (i + 1) / len(df)
            progress_bar.progress(progress, text=f"Analyzing transaction {i+1}/{len(df)}...")

            try:
                features_df = extractor.extract_from_manual_input(
                    transaction_amount=float(row.get("Transaction_Amount", 0)),
                    account_balance=float(row.get("Account_Balance", 50000)),
                    age=int(row.get("Age", 30)),
                    account_type=str(row.get("Account_Type", "Savings")),
                    transaction_type=str(row.get("Transaction_Type", "Debit")),
                    merchant_category=str(row.get("Merchant_Category", "Groceries")),
                    device_type=str(row.get("Device_Type", "Mobile")),
                    transaction_device=str(row.get("Transaction_Device", "Mobile Device")),
                    hour=int(row.get("Hour", 12)),
                    day_of_week=int(row.get("DayOfWeek", 2)),
                )

                prediction = prediction_engine.predict(features_df)

                results.append({
                    "amount": float(row.get("Transaction_Amount", 0)),
                    "transaction_type": str(row.get("Transaction_Type", "N/A")),
                    "label": prediction["label"],
                    "confidence": prediction["confidence"],
                    "risk_score": prediction["risk_score"],
                    "risk_tier": prediction["risk_tier"],
                })

            except Exception as e:
                errors.append({"row": i + 1, "error": str(e)})

        progress_bar.progress(1.0, text="✅ Batch analysis complete!")

        # Display results
        if results:
            st.markdown("### 📊 Results")
            results_df = pd.DataFrame(results)
            results_df.columns = ["Amount", "Type", "Label", "Confidence", "Risk Score", "Risk Tier"]
            results_df["Confidence"] = results_df["Confidence"].apply(lambda x: f"{x:.1%}")

            st.dataframe(results_df, use_container_width=True, hide_index=True)

            # Summary
            fraud_count = sum(1 for r in results if r["label"] == "fraud")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Analyzed", len(results))
            col2.metric("Fraudulent", fraud_count)
            col3.metric("Legitimate", len(results) - fraud_count)

            # Downloads
            st.markdown("### 📥 Download Results")
            col_a, col_b = st.columns(2)

            with col_a:
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    "📄 Download CSV", data=csv_data,
                    file_name="batch_results.csv", mime="text/csv",
                )

            with col_b:
                try:
                    gen = ReportGenerator()
                    pdf_bytes = gen.generate_batch_report(
                        results=results,
                        generated_by=st.session_state.get("username", "System"),
                    )
                    st.download_button(
                        "📄 Download PDF", data=pdf_bytes,
                        file_name="batch_report.pdf", mime="application/pdf",
                    )
                except Exception:
                    pass

        if errors:
            with st.expander(f"⚠️ {len(errors)} errors"):
                for err in errors:
                    st.write(f"- Row {err['row']}: {err['error']}")
