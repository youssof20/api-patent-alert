"""
Admin authentication for Streamlit dashboard
"""
import streamlit as st
import hashlib
from app.config import settings


def check_admin_password():
    """Check if user is authenticated as admin"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("Admin Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Simple password check (in production, use proper auth)
            if username == settings.admin_username and password == settings.admin_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.stop()
    
    return True


def logout():
    """Logout admin user"""
    st.session_state.authenticated = False
    st.rerun()

