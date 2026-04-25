"""
auth.py — Login & Signup pages for Fraud Detection System.

Uses bcrypt for password hashing and st.session_state for session management.
"""

import re
import streamlit as st


def show_login_page(db):
    """Render the login page."""

    # Centered card layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <h1 style="color: #0d6efd; margin-bottom: 0.2rem;">🏦</h1>
            <h2 style="color: #212529; margin-bottom: 0.2rem;">Fraud Detection System</h2>
            <p style="color: #6c757d;">Sign in to your account</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="admin@example.com",
                                  key="login_email")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter your password",
                                     key="login_password")

            submitted = st.form_submit_button("🔐 Sign In", type="primary",
                                               use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = db.authenticate(email.strip(), password)
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user["userId"]
                        st.session_state["username"] = user["username"]
                        st.session_state["email"] = user["email"]
                        st.session_state["is_admin"] = user["is_admin"]
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")

        # Switch to signup
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #6c757d;'>Don't have an account?</p>",
            unsafe_allow_html=True,
        )
        if st.button("📝 Create Account", use_container_width=True,
                      key="go_to_signup"):
            st.session_state["show_signup"] = True
            st.rerun()


def show_signup_page(db):
    """Render the signup page."""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <h1 style="color: #0d6efd; margin-bottom: 0.2rem;">🏦</h1>
            <h2 style="color: #212529; margin-bottom: 0.2rem;">Create Account</h2>
            <p style="color: #6c757d;">Register for a new account</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("signup_form", clear_on_submit=True):
            username = st.text_input("Username", placeholder="johndoe",
                                     key="signup_username")
            email = st.text_input("Email", placeholder="john@example.com",
                                  key="signup_email")
            password = st.text_input("Password", type="password",
                                     placeholder="Min 6 characters",
                                     key="signup_password")
            password2 = st.text_input("Confirm Password", type="password",
                                      placeholder="Repeat password",
                                      key="signup_password2")

            submitted = st.form_submit_button("📝 Create Account",
                                               type="primary",
                                               use_container_width=True)

            if submitted:
                # Validations
                errors = []
                if not username or not email or not password:
                    errors.append("All fields are required.")
                if len(username) < 3:
                    errors.append("Username must be at least 3 characters.")
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    errors.append("Please enter a valid email address.")
                if len(password) < 6:
                    errors.append("Password must be at least 6 characters.")
                if password != password2:
                    errors.append("Passwords do not match.")
                if db.user_exists(username=username):
                    errors.append("Username already taken.")
                if db.user_exists(email=email):
                    errors.append("Email already registered.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    try:
                        user = db.create_user(username.strip(), email.strip(), password)
                        st.success("✅ Account created! You can now sign in.")
                        st.session_state["show_signup"] = False
                    except Exception as e:
                        st.error(f"Registration failed: {e}")

        # Switch back to login
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: #6c757d;'>Already have an account?</p>",
            unsafe_allow_html=True,
        )
        if st.button("🔐 Back to Sign In", use_container_width=True,
                      key="go_to_login"):
            st.session_state["show_signup"] = False
            st.rerun()


def logout():
    """Clear session state and logout."""
    keys_to_clear = [
        "authenticated", "user_id", "username", "email", "is_admin",
        "show_signup", "training_data", "trained_models", "metrics_df",
        "evaluator", "trainer",
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
