"""
dashboard.py — Main dual-tab dashboard for Fraud Detection System.

Tab 1: Manual Transaction Entry — input form → prediction → risk assessment
Tab 2: Real-Time Transaction Monitor — simulated live scoring feed
"""

import json
import time
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.feature_extractor import (
    FeatureExtractor, ACCOUNT_TYPE_CATEGORIES,
    TRANSACTION_TYPE_CATEGORIES, MERCHANT_CATEGORY_CATEGORIES,
    DEVICE_TYPE_CATEGORIES, TRANSACTION_DEVICE_CATEGORIES,
)
from core.prediction_engine import PredictionEngine
from core.history_manager import HistoryManager
from core.alert_simulator import AlertSimulator
from core.report_generator import ReportGenerator


DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]


def show_dashboard(db, prediction_engine: PredictionEngine,
                   history_manager: HistoryManager):
    """Render the main dashboard with two tabs."""

    st.markdown("## 🏦 Fraud Detection Dashboard")

    if not prediction_engine.is_ready():
        st.warning(
            "⚠️ **Model not loaded.** An admin needs to train the model first "
            "via **Model Training** page. Manual entry will not work until "
            "a model is saved to `models/best_model.pkl`."
        )

    tab1, tab2 = st.tabs(["📝 Manual Entry", "📡 Real-Time Monitor"])

    # ══════════════════════════════════════════════════════════════════
    # TAB 1: Manual Transaction Entry
    # ══════════════════════════════════════════════════════════════════
    with tab1:
        _show_manual_entry(db, prediction_engine, history_manager)

    # ══════════════════════════════════════════════════════════════════
    # TAB 2: Real-Time Transaction Monitor
    # ══════════════════════════════════════════════════════════════════
    with tab2:
        _show_realtime_monitor(prediction_engine)


def _show_manual_entry(db, prediction_engine, history_manager):
    """Manual transaction entry form and prediction display."""

    st.markdown("### Enter Transaction Details")
    st.markdown("Fill in the transaction details below to check for fraud.")

    with st.form("transaction_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            account_number = st.text_input("Account Number", placeholder="e.g. 1234567890")
            amount = st.number_input("Transaction Amount (₹)", min_value=10.0,
                                     max_value=99000.0, value=25000.0, step=1.0)
            account_type = st.selectbox("Account Type", ACCOUNT_TYPE_CATEGORIES)
            merchant_cat = st.selectbox("Merchant Category", MERCHANT_CATEGORY_CATEGORIES)
            device_type = st.selectbox("Device Type", DEVICE_TYPE_CATEGORIES)
            age = st.number_input("Customer Age", min_value=18, max_value=70, value=35)

        with col2:
            customer_email = st.text_input("Customer Email", placeholder="e.g. user@email.com")
            balance = st.number_input("Account Balance (₹)", min_value=5000.0,
                                      max_value=100000.0, value=50000.0, step=1.0)
            txn_type = st.selectbox("Transaction Type", TRANSACTION_TYPE_CATEGORIES)
            txn_device = st.selectbox("Transaction Device", TRANSACTION_DEVICE_CATEGORIES)
            day_name = st.selectbox("Day of Week", DAYS_OF_WEEK)
            day_of_week = DAYS_OF_WEEK.index(day_name)
            
            st.markdown("**Transaction Time**")
            time_col1, time_col2, time_col3 = st.columns(3)
            # Determine current 12-hour defaults
            _now = datetime.now()
            _default_h12 = _now.hour % 12 or 12
            _default_period = "AM" if _now.hour < 12 else "PM"
            with time_col1:
                txn_hour_12 = st.selectbox(
                    "Hour", options=list(range(1, 13)),
                    index=_default_h12 - 1, key="txn_hour_12"
                )
            with time_col2:
                minute_options = [f"{m:02d}" for m in range(60)]
                txn_minute = st.selectbox(
                    "Minute", options=minute_options,
                    index=_now.minute, key="txn_minute"
                )
            with time_col3:
                txn_period = st.selectbox(
                    "AM / PM", options=["AM", "PM"],
                    index=0 if _default_period == "AM" else 1,
                    key="txn_period"
                )

        submitted = st.form_submit_button("🔍 Analyze Transaction",
                                           type="primary",
                                           use_container_width=True)

    if submitted and prediction_engine.is_ready():
        if amount > balance:
            st.warning("⚠️ **Warning:** Transaction Amount cannot be greater than the Account Balance!")
            return

        # Convert 12-hour AM/PM to 24-hour format
        if txn_period == "AM":
            hour = 0 if txn_hour_12 == 12 else txn_hour_12
        else:
            hour = 12 if txn_hour_12 == 12 else txn_hour_12 + 12

        # Load feature extractor from disk if available
        import os, joblib
        extractor_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models", "feature_extractor.pkl"
        )
        if os.path.exists(extractor_path):
            extractor = joblib.load(extractor_path)
        else:
            extractor = FeatureExtractor()

        # Extract features
        features_df = extractor.extract_from_manual_input(
            transaction_amount=amount,
            account_balance=balance,
            age=age,
            account_type=account_type,
            transaction_type=txn_type,
            merchant_category=merchant_cat,
            device_type=device_type,
            transaction_device=txn_device,
            hour=hour,
            day_of_week=day_of_week,
        )

        # Raw values for risk assessment and reporting
        raw_values = {
            "Account_Number": account_number if account_number else "N/A",
            "Customer_Email": customer_email if customer_email else "N/A",
            "Transaction_Amount": amount,
            "Account_Balance": balance,
            "Age": age,
            "Account_Type": account_type,
            "Transaction_Type": txn_type,
            "Merchant_Category": merchant_cat,
            "Device_Type": device_type,
            "Transaction_Device": txn_device,
            "Hour": hour,
            "Time": f"{txn_hour_12}:{txn_minute} {txn_period}",
            "Day_Of_Week": day_name,
        }

        # Predict
        prediction = prediction_engine.predict(features_df, raw_values)

        # --- Display Results ---
        st.markdown("---")
        _display_prediction_results(prediction, raw_values, db, history_manager)

    elif submitted and not prediction_engine.is_ready():
        st.error("❌ Model not loaded. Train the model first via Admin → Model Training.")


def _display_prediction_results(prediction, raw_values, db, history_manager):
    """Display prediction results with charts, risk flags, and alerts."""

    label = prediction["label"]
    confidence = prediction["confidence"]
    risk_score = prediction["risk_score"]
    risk_tier = prediction["risk_tier"]

    # Result card
    if label == "fraud":
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                    color: white; padding: 1.5rem; border-radius: 12px;
                    text-align: center; margin: 1rem 0;">
            <h2 style="margin: 0; color: white;">🚫 FRAUDULENT</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; color: rgba(255,255,255,0.9);">
                Confidence: {confidence:.1%} | Risk Score: {risk_score}/100 ({risk_tier})
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #198754 0%, #157347 100%);
                    color: white; padding: 1.5rem; border-radius: 12px;
                    text-align: center; margin: 1rem 0;">
            <h2 style="margin: 0; color: white;">✅ LEGITIMATE</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; color: rgba(255,255,255,0.9);">
                Confidence: {confidence:.1%} | Risk Score: {risk_score}/100 ({risk_tier})
            </p>
        </div>
        """, unsafe_allow_html=True)

    if prediction.get("low_confidence"):
        st.warning("⚠️ Low confidence prediction — results may not be reliable.")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prediction", label.upper())
    col2.metric("Confidence", f"{confidence:.1%}")
    col3.metric("Risk Score", f"{risk_score}/100")
    col4.metric("Risk Tier", risk_tier)

    # Confidence gauge
    st.markdown("#### Confidence Gauge")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prediction.get("fraud_probability", 0) * 100,
        title={"text": "Fraud Probability"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#dc3545" if label == "fraud" else "#198754"},
            "steps": [
                {"range": [0, 25], "color": "#d4edda"},
                {"range": [25, 50], "color": "#fff3cd"},
                {"range": [50, 75], "color": "#fde2e2"},
                {"range": [75, 100], "color": "#f8d7da"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 50,
            },
        },
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Risk flags
    risk_flags = prediction.get("risk_flags", {})
    if risk_flags:
        st.markdown("#### Risk Assessment")
        for feature, info in risk_flags.items():
            st.write(f"{info['flag']} **{feature}**: {info['note']}")

    # SHAP values
    shap_values = prediction.get("shap_values", {})
    if shap_values:
        st.markdown("#### Feature Importance (SHAP)")
        sorted_shap = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:15]
        names = [s[0] for s in sorted_shap]
        values = [s[1] for s in sorted_shap]

        fig_shap = go.Figure(go.Bar(
            x=values, y=names, orientation="h",
            marker_color=["#dc3545" if v > 0 else "#198754" for v in values],
        ))
        fig_shap.update_layout(
            title="Top Features Influencing Prediction",
            xaxis_title="SHAP Value (→ Fraud | ← Legitimate)",
            template="plotly_white", height=400,
        )
        st.plotly_chart(fig_shap, use_container_width=True)

    # Email alert (fraud only)
    if label == "fraud":
        st.markdown("#### 📧 Email Alert Simulation")
        alert = AlertSimulator.generate_alert(raw_values, prediction)
        alert_color = AlertSimulator.get_alert_severity_color(risk_tier)
        st.markdown(f"""
        <div style="background: #1a1a2e; color: #00ff41; font-family: monospace;
                    padding: 1rem; border-radius: 8px; border-left: 4px solid {alert_color};
                    white-space: pre-wrap; font-size: 0.85rem; overflow-x: auto;">
{alert}
        </div>
        """, unsafe_allow_html=True)

    # Save to history
    try:
        txn_summary = json.dumps(raw_values, default=str)
        history_manager.save_result(
            user_id=st.session_state.get("user_id", ""),
            transaction_details=txn_summary,
            label=label,
            risk_score=risk_score,
            confidence=confidence,
            shap_values=shap_values,
        )
    except Exception as e:
        print(f"[HISTORY] Save failed: {e}")

    # PDF download
    st.markdown("#### 📥 Download Report")
    try:
        gen = ReportGenerator()
        pdf_bytes = gen.generate_single_report(
            transaction=raw_values,
            prediction=prediction,
            generated_by=st.session_state.get("username", "System"),
        )
        st.download_button(
            "📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"transaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.warning(f"PDF generation failed: {e}")


def _show_realtime_monitor(prediction_engine):
    """Simulated real-time transaction monitoring dashboard."""

    st.markdown("### 📡 Real-Time Transaction Monitor")
    st.markdown("Simulated live transaction feed — scoring transactions in real-time.")

    if not prediction_engine.is_ready():
        st.warning("⚠️ Model not loaded. Train the model first.")
        return

    # Controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        num_transactions = st.number_input("Transactions to scan", 5, 50, 20)
    with col2:
        scan_speed = st.selectbox("Speed", ["Fast", "Normal", "Slow"])

    speed_map = {"Fast": 0.1, "Normal": 0.3, "Slow": 0.8}

    if st.button("▶️ Start Monitoring", type="primary", key="start_monitor"):
        import os, joblib
        extractor_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models", "feature_extractor.pkl"
        )
        if os.path.exists(extractor_path):
            extractor = joblib.load(extractor_path)
        else:
            extractor = FeatureExtractor()

        # Initialize
        results = []
        progress_bar = st.progress(0, text="Initializing monitor...")
        stats_container = st.empty()
        table_container = st.empty()

        for i in range(num_transactions):
            # Generate random transaction
            txn = FeatureExtractor.generate_random_transaction()
            features_df = extractor.extract_from_manual_input(**txn)
            prediction = prediction_engine.predict(features_df, txn)

            results.append({
                "#": i + 1,
                "Amount": f"₹{txn['Transaction_Amount']:,.0f}",
                "Type": txn["Transaction_Type"],
                "Device": txn["Device_Type"],
                "Label": prediction["label"].upper(),
                "Risk": prediction["risk_score"],
                "Confidence": f"{prediction['confidence']:.0%}",
            })

            # Update progress
            progress = (i + 1) / num_transactions
            progress_bar.progress(progress, text=f"Scanning transaction {i+1}/{num_transactions}...")

            # Update stats
            fraud_count = sum(1 for r in results if r["Label"] == "FRAUD")
            total = len(results)

            with stats_container.container():
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Scanned", total)
                c2.metric("Fraud Detected", fraud_count)
                c3.metric("Fraud Rate", f"{fraud_count/max(total,1)*100:.1f}%")
                c4.metric("Avg Risk", f"{sum(r['Risk'] for r in results)/max(total,1):.0f}")

            # Update table
            df = pd.DataFrame(results)
            table_container.dataframe(df, use_container_width=True, hide_index=True)

            time.sleep(speed_map.get(scan_speed, 0.3))

        progress_bar.progress(1.0, text="✅ Monitoring complete!")
        st.success(f"Scanned {num_transactions} transactions — {fraud_count} flagged as fraud.")
