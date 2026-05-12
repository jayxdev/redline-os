import streamlit as st
import os
import extra_streamlit_components as stx
from datetime import datetime, timedelta

def get_cookie_manager():
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key="redline_cookie_manager")
    return st.session_state.cookie_manager

def check_password():
    """Returns `True` if the user had the correct password (via session or cookie)."""
    
    from redline.core.config_service import ConfigService
    config = ConfigService()
    cookie_manager = get_cookie_manager()
    correct_password = config.get("APP_PASSWORD", "admin")
    
    # Check if already authenticated in session
    if st.session_state.get("password_correct"):
        return True
    
    # Check if authenticated via cookie
    auth_cookie = cookie_manager.get("redline_auth")
    if auth_cookie == correct_password:
        st.session_state["password_correct"] = True
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        user_input = st.session_state.get("password_input")
        if not user_input:
            return
            
        if user_input == correct_password:
            st.session_state["password_correct"] = True
            # Set cookie to expire in 24 hours
            cookie_manager.set("redline_auth", correct_password, expires_at=datetime.now() + timedelta(days=1))
            if "password_input" in st.session_state:
                del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    # Show login form
    st.title("🏎️ Redline Cult Login")
    st.text_input(
        "Enter system password to continue", 
        type="password", 
        on_change=password_entered, 
        key="password_input"
    )
    
    if st.session_state.get("password_correct") == False:
        st.error("😕 Password incorrect")
        
    return False

def logout():
    """Clears authentication state and cookies."""
    cookie_manager = get_cookie_manager()
    cookie_manager.delete("redline_auth")
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    st.rerun()
