"""
history.py — Analysis History page.

View, filter, delete, and export past transaction analysis results.
"""

from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

from core.history_manager import HistoryManager


def show_history_page(history_manager: HistoryManager):
    """Render the analysis history page."""
    st.markdown("## 📜 Analysis History")
    st.markdown("View and manage your past transaction analyses.")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Not logged in.")
        return

    # Date filters
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        start_date = st.date_input(
            "From", value=datetime.now() - timedelta(days=30),
            key="history_start_date",
        )
    with col2:
        end_date = st.date_input(
            "To", value=datetime.now(),
            key="history_end_date",
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔍 Filter", use_container_width=True, key="history_filter_btn")

    # Convert dates
    start_str = start_date.isoformat() if start_date else None
    end_str = (end_date.isoformat() + "T23:59:59") if end_date else None

    # Fetch records
    records = history_manager.get_user_history(user_id, start_str, end_str)

    if not records:
        st.info("📭 No analysis history found for the selected date range.")
        return

    st.markdown(f"**{len(records)}** records found")

    # Display table
    display_data = []
    for r in records:
        display_data.append({
            "historyId": r["historyId"],
            "Label": r.get("resultLabel", "N/A").upper(),
            "Risk Score": r.get("riskScore", "N/A"),
            "Confidence": f"{r.get('confidenceScore', 0):.1%}",
            "Date": str(r.get("predictedAt", "N/A"))[:19],
            "Exported As": r.get("exportedAs", "none"),
        })

    df = pd.DataFrame(display_data)
    st.dataframe(
        df[["Label", "Risk Score", "Confidence", "Date", "Exported As"]],
        use_container_width=True, hide_index=True,
    )

    # Delete records
    st.markdown("---")
    st.markdown("### 🗑️ Delete Records")

    delete_options = {f"{r['Label']} — {r['Date']}": r["historyId"]
                      for r in display_data}

    selected = st.selectbox(
        "Select record to delete",
        options=["— Select —"] + list(delete_options.keys()),
        key="delete_record_select",
    )

    if st.button("🗑️ Delete Selected", type="secondary", key="delete_record_btn"):
        if selected != "— Select —":
            history_id = delete_options[selected]
            if history_manager.delete_record(history_id, user_id):
                st.success("Record deleted!")
                st.rerun()
            else:
                st.error("Failed to delete.")
        else:
            st.warning("Please select a record.")

    # Export
    st.markdown("---")
    st.markdown("### 📥 Export History")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("📄 Export as CSV", use_container_width=True, key="export_csv_btn"):
            csv_data = history_manager.export_csv(records)
            st.download_button(
                "⬇️ Download CSV", data=csv_data,
                file_name="analysis_history.csv", mime="text/csv",
                key="csv_download_btn",
            )

    with col_b:
        if st.button("📄 Export as PDF", use_container_width=True, key="export_pdf_btn"):
            username = st.session_state.get("username", "User")
            pdf_bytes = history_manager.export_pdf(records, username)
            st.download_button(
                "⬇️ Download PDF", data=pdf_bytes,
                file_name="analysis_history.pdf", mime="application/pdf",
                key="pdf_download_btn",
            )
