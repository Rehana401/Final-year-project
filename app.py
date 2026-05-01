"""
Fraud Detection in Online Banking System
=========================================
Main Streamlit application entry point.

Features:
  • Dual-interface: User Dashboard + Admin Dashboard
  • Authentication: Login/Signup with bcrypt hashing
  • ML Pipeline: Train, tune, and deploy fraud detection models
  • Real-time monitoring, PDF reports, email alert simulation

Run: streamlit run app.py
"""

import os
import sys
import streamlit as st

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.database import DatabaseManager
from core.prediction_engine import PredictionEngine
from core.history_manager import HistoryManager
from components.auth import show_login_page, show_signup_page, logout


# ══════════════════════════════════════════════════════════════════════
# Page configuration
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    /* Global styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #1a1a2e 100%);
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e2e8f0;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
    }

    /* Button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0d6efd 0%, #0856d6 100%);
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Form styling */
    [data-testid="stForm"] {
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
    }

    /* Hide 'Press Enter to submit form' text inside inputs */
    div[data-testid="InputInstructions"] > span,
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
    }

    /* Hide default hamburger */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# Initialize services (cached)
# ══════════════════════════════════════════════════════════════════════
@st.cache_resource
def init_database():
    """Initialize database (cached across sessions)."""
    return DatabaseManager()


@st.cache_resource
def init_prediction_engine():
    """Initialize prediction engine (cached)."""
    return PredictionEngine()


def init_services():
    """Initialize all application services."""
    db = init_database()
    prediction_engine = init_prediction_engine()
    history_manager = HistoryManager(db)
    return db, prediction_engine, history_manager


# ══════════════════════════════════════════════════════════════════════
# Authentication gate
# ══════════════════════════════════════════════════════════════════════
def check_auth(db):
    """Check if user is authenticated. Show login/signup if not."""
    if not st.session_state.get("authenticated", False):
        if st.session_state.get("show_signup", False):
            show_signup_page(db)
        else:
            show_login_page(db)
        st.stop()


# ══════════════════════════════════════════════════════════════════════
# Sidebar navigation
# ══════════════════════════════════════════════════════════════════════
def render_sidebar(db, prediction_engine):
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #0d6efd; margin: 0;">🏦</h2>
            <h3 style="color: #e2e8f0; margin: 0.3rem 0;">Fraud Detection</h3>
            <p style="color: #94a3b8; font-size: 0.85rem;">Online Banking System</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User info
        username = st.session_state.get("username", "User")
        is_admin = st.session_state.get("is_admin", False)
        role = "🔑 Admin" if is_admin else "👤 User"

        st.markdown(f"""
        <div style="background: rgba(13, 110, 253, 0.15); padding: 0.8rem;
                    border-radius: 8px; margin-bottom: 1rem;">
            <p style="color: #e2e8f0; margin: 0; font-weight: 600;">
                {role} — {username}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation buttons
        st.markdown("### Navigation")

        page = st.radio(
            "Go to",
            options=[
                "🏦 Dashboard",
                "📦 Batch Analysis",
                "📜 Analysis History",
                "📊 Dataset Insights",
                "🧠 Model Training",
            ],
            label_visibility="collapsed",
            key="nav_radio",
        )

        # Admin gate for restricted pages
        if page in ["📊 Dataset Insights", "🧠 Model Training"] and not is_admin:
            st.warning("🔒 Admin access required")

        st.markdown("---")

        # System stats
        st.markdown("### System Stats")
        col1, col2 = st.columns(2)
        col1.metric("Users", db.get_user_count())
        col2.metric("Analyses", db.get_total_analyses())

        model_status = "✅ Ready" if prediction_engine.is_ready() else "❌ Not trained"
        st.markdown(f"**Model:** {model_status}")

        if prediction_engine.is_ready():
            if st.button("🔄 Reload Model", use_container_width=True, key="reload_model"):
                prediction_engine.reload()
                st.success("Model reloaded!")
                st.rerun()

        st.markdown("---")

        # Logout
        if st.button("🚪 Logout", use_container_width=True, type="secondary",
                      key="logout_btn"):
            logout()
            st.rerun()

    return page


# ══════════════════════════════════════════════════════════════════════
# Main app
# ══════════════════════════════════════════════════════════════════════
def main():
    """Main application entry point."""
    db, prediction_engine, history_manager = init_services()

    # Auth gate
    check_auth(db)

    # Sidebar + navigation
    page = render_sidebar(db, prediction_engine)

    # Page routing
    if page == "🏦 Dashboard":
        from components.dashboard import show_dashboard
        show_dashboard(db, prediction_engine, history_manager)

    elif page == "📦 Batch Analysis":
        from components.batch import show_batch_page
        show_batch_page(db, prediction_engine, history_manager)

    elif page == "📜 Analysis History":
        from components.history import show_history_page
        show_history_page(history_manager)

    elif page == "📊 Dataset Insights":
        from components.dataset_insights import show_dataset_insights
        show_dataset_insights(db)

    elif page == "🧠 Model Training":
        from components.model_training import show_model_training
        show_model_training(db)


if __name__ == "__main__":
    main()
