"""
dataset_insights.py — Admin-only Dataset Insight Dashboard.

Visualizes dataset statistics, feature distributions, correlations,
fraud trends by category, and model comparisons.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

from ml.data_manager import DataManager


def show_dataset_insights(db):
    """Render the dataset insight dashboard (admin only)."""

    if not st.session_state.get("is_admin"):
        st.error("🔒 This page is restricted to administrators.")
        st.stop()

    st.markdown("## 📊 Dataset Insight Dashboard")
    st.markdown("Explore the Bank Transaction Fraud Detection dataset and model performance.")

    # Load dataset
    dm = DataManager()
    try:
        with st.spinner("Loading dataset..."):
            df = dm.load_dataset()
            df_clean = dm.clean()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        return

    info = dm.get_info()
    label_col = info["label_column"]

    # ── Section A: Dataset Overview ──
    st.markdown("### 📋 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{info['rows']:,}")
    col2.metric("Features", info['columns'])
    col3.metric("Missing Values", info['total_missing'])
    col4.metric("Duplicates", info['duplicates'])

    # Class distribution
    st.markdown("#### Class Distribution")
    dist = info["label_distribution"]
    col_a, col_b = st.columns(2)

    with col_a:
        fig_pie = px.pie(
            names=["Legitimate (0)", "Fraud (1)"],
            values=[dist.get(0, 0), dist.get(1, 0)],
            color_discrete_sequence=["#198754", "#dc3545"],
            title="Label Distribution",
        )
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        fig_bar = px.bar(
            x=["Legitimate (0)", "Fraud (1)"],
            y=[dist.get(0, 0), dist.get(1, 0)],
            color=["Legitimate", "Fraud"],
            color_discrete_map={"Legitimate": "#198754", "Fraud": "#dc3545"},
            title="Label Counts",
        )
        fig_bar.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    total = sum(dist.values())
    fraud_pct = dist.get(1, 0) / total * 100
    st.warning(f"⚠️ Dataset is imbalanced — fraud rate is **{fraud_pct:.2f}%**. SMOTE will be applied during training.")

    # ── Section B: Fraud Trend Analysis ──
    st.markdown("---")
    st.markdown("### 📈 Fraud Trend Analysis")

    # Fraud by Transaction Type
    col1, col2 = st.columns(2)

    with col1:
        fraud_by_type = df.groupby("Transaction_Type")["Is_Fraud"].mean().sort_values(ascending=False) * 100
        fig_type = px.bar(
            x=fraud_by_type.index, y=fraud_by_type.values,
            title="Fraud Rate by Transaction Type",
            labels={"x": "Transaction Type", "y": "Fraud Rate (%)"},
            color=fraud_by_type.values,
            color_continuous_scale="Reds",
        )
        fig_type.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        fraud_by_cat = df.groupby("Merchant_Category")["Is_Fraud"].mean().sort_values(ascending=False) * 100
        fig_cat = px.bar(
            x=fraud_by_cat.index, y=fraud_by_cat.values,
            title="Fraud Rate by Merchant Category",
            labels={"x": "Merchant Category", "y": "Fraud Rate (%)"},
            color=fraud_by_cat.values,
            color_continuous_scale="Reds",
        )
        fig_cat.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fraud_by_dev = df.groupby("Device_Type")["Is_Fraud"].mean().sort_values(ascending=False) * 100
        fig_dev = px.bar(
            x=fraud_by_dev.index, y=fraud_by_dev.values,
            title="Fraud Rate by Device Type",
            labels={"x": "Device Type", "y": "Fraud Rate (%)"},
            color=fraud_by_dev.values,
            color_continuous_scale="Reds",
        )
        fig_dev.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_dev, use_container_width=True)

    with col4:
        # Fraud by Hour of Day
        df["Hour"] = pd.to_datetime(df["Transaction_Time"], format="%H:%M:%S", errors="coerce").dt.hour
        fraud_by_hour = df.groupby("Hour")["Is_Fraud"].mean() * 100
        fig_hour = px.line(
            x=fraud_by_hour.index, y=fraud_by_hour.values,
            title="Fraud Rate by Hour of Day",
            labels={"x": "Hour (0-23)", "y": "Fraud Rate (%)"},
            markers=True,
        )
        fig_hour.update_layout(height=350)
        st.plotly_chart(fig_hour, use_container_width=True)

    # ── Section C: Feature Distributions ──
    st.markdown("---")
    st.markdown("### 📊 Feature Distributions")

    numeric_features = ["Transaction_Amount", "Account_Balance", "Age"]
    for feature in numeric_features:
        with st.expander(f"📊 {feature}"):
            col1, col2 = st.columns(2)

            df["Is_Fraud_Label"] = df["Is_Fraud"].map({0: "Legitimate", 1: "Fraud"})

            with col1:
                fig_hist = px.histogram(
                    df, x=feature, color="Is_Fraud_Label",
                    color_discrete_map={"Legitimate": "#198754", "Fraud": "#dc3545"},
                    barmode="overlay", opacity=0.7,
                    title=f"{feature} — Histogram",
                    marginal="rug",
                )
                fig_hist.update_layout(height=350)
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                fig_box = px.box(
                    df, x="Is_Fraud_Label", y=feature, color="Is_Fraud_Label",
                    color_discrete_map={"Legitimate": "#198754", "Fraud": "#dc3545"},
                    title=f"{feature} — Box Plot",
                )
                fig_box.update_layout(height=350)
                st.plotly_chart(fig_box, use_container_width=True)

    # ── Section D: Correlation Heatmap ──
    st.markdown("---")
    st.markdown("### 🔗 Correlation Heatmap")

    numeric_df = df[["Transaction_Amount", "Account_Balance", "Age", "Is_Fraud"]].copy()
    corr_matrix = numeric_df.corr()

    fig_corr, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr_matrix, annot=True, fmt=".3f", cmap="RdBu_r",
        center=0, ax=ax, linewidths=0.5, square=True,
    )
    ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    st.pyplot(fig_corr)

    # ── Section E: Model Comparison ──
    all_models = db.get_all_models()
    if all_models:
        st.markdown("---")
        st.markdown("### 🏆 Model Comparison")

        model_df = pd.DataFrame(all_models)
        display_cols = ["algorithmType", "accuracy", "precision_score", "recall", "f1Score", "aucRoc", "isBestModel"]
        available_cols = [c for c in display_cols if c in model_df.columns]
        st.dataframe(model_df[available_cols], use_container_width=True, hide_index=True)
    else:
        st.markdown("---")
        st.info("💡 Train models via **Model Training** page to see comparison metrics here.")
