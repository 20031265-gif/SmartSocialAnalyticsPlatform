import streamlit as st
import requests
from firebase_config import db_firestore

FIREBASE_WEB_API_KEY = "AIzaSyBfXbYCsa_deF1l4vJ8ZLsrySIOVTIJOys"

SIGN_UP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
SIGN_IN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"


# ============================================================
# ERROR HANDLER
# ============================================================

def firebase_error_message(code):
    errors = {
        "EMAIL_EXISTS": "An account with this email already exists.",
        "EMAIL_NOT_FOUND": "No account was found with this email address.",
        "INVALID_PASSWORD": "Incorrect password.",
        "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
        "USER_DISABLED": "This account has been disabled.",
        "INVALID_EMAIL": "Please enter a valid email address.",
        "WEAK_PASSWORD": "Password must be at least 6 characters long.",
        "OPERATION_NOT_ALLOWED": "Email/password authentication is not enabled.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Try again later.",
        "USER_NOT_FOUND": "User account not found."
    }
    return errors.get(code, "Authentication error. Please try again.")


# ============================================================
# GET USER DATA (from Firestore)
# ============================================================

def get_user_data(uid):
    doc = db_firestore.collection("users").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None


# ============================================================
# REGISTER (NO VERIFICATION)
# ============================================================

def register():
    st.subheader("📝 Create an Account")

    name = st.text_input("Full Name")
    role = st.selectbox("Select Role", ["User", "Admin"])
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("📝 Create Account", type="primary"):

        if not name or not email or not password:
            st.error("All fields are required.")
            return

        if password != confirm:
            st.error("Passwords do not match.")
            return

        try:
            response = requests.post(
                SIGN_UP_URL,
                json={"email": email, "password": password, "returnSecureToken": True}
            )
            data = response.json()

            if response.status_code != 200:
                st.error(firebase_error_message(data.get("error", {}).get("message", "")))
                return

            uid = data["localId"]

            db_firestore.collection("users").document(uid).set({
                "uid": uid,
                "name": name,
                "email": email,
                "role": role
            })

            st.success("Account created successfully!")

        except Exception as e:
            st.error(f"Registration error: {str(e)}")


# ============================================================
# LOGIN (NO VERIFICATION)
# ============================================================

def login():
    st.subheader("🔐 Login")

    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("🔐 Login", type="primary"):

        if not email or not password:
            st.error("Please enter both email and password.")
            return

        try:
            response = requests.post(
                SIGN_IN_URL,
                json={"email": email, "password": password, "returnSecureToken": True}
            )
            data = response.json()

            if response.status_code != 200:
                st.error(firebase_error_message(data.get("error", {}).get("message", "")))
                return

            uid = data["localId"]

            user_data = get_user_data(uid)

            if not user_data:
                st.error("User data not found in Firestore.")
                return

            st.session_state["logged_in"] = True
            st.session_state["user"] = user_data
            st.session_state["redirect_dashboard"] = True

            st.success(f"Welcome back, {user_data['name']}!")
            st.rerun()

        except Exception as e:
            st.error(f"Login error: {str(e)}")
