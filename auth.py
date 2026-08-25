import streamlit as st
import requests
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_config import db


# ============================================================
# FIREBASE WEB API KEY
# ============================================================
# Get this from:
# Firebase Console
# → Project Settings
# → General
# → Your apps
# → Web API Key
#
# IMPORTANT:
# This is NOT the private_key from firebase_key.json.

FIREBASE_WEB_API_KEY = "AIzaSyBfXbYCsa_deF1l4vJ8ZLsrySIOVTIJOys"


# ============================================================
# FIREBASE AUTH URLS
# ============================================================

SIGN_UP_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    "?key=" + FIREBASE_WEB_API_KEY
)

SIGN_IN_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    "?key=" + FIREBASE_WEB_API_KEY
)

PASSWORD_RESET_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
    "?key=" + FIREBASE_WEB_API_KEY
)

LOOKUP_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:lookup"
    "?key=" + FIREBASE_WEB_API_KEY
)


# ============================================================
# FIREBASE ERROR HANDLER
# ============================================================

def firebase_error_message(error_code):

    errors = {

        "EMAIL_EXISTS":
            "An account with this email already exists.",

        "EMAIL_NOT_FOUND":
            "No account was found with this email address.",

        "INVALID_PASSWORD":
            "Incorrect password.",

        "INVALID_LOGIN_CREDENTIALS":
            "Incorrect email or password.",

        "USER_DISABLED":
            "This account has been disabled.",

        "INVALID_EMAIL":
            "Please enter a valid email address.",

        "WEAK_PASSWORD":
            "Password must be at least 6 characters long.",

        "OPERATION_NOT_ALLOWED":
            "Email/password authentication is not enabled in Firebase.",

        "TOO_MANY_ATTEMPTS_TRY_LATER":
            "Too many attempts. Please try again later.",

        "INVALID_ID_TOKEN":
            "Your session has expired. Please log in again.",

        "USER_NOT_FOUND":
            "User account not found."

    }

    return errors.get(
        error_code,
        "Authentication error. Please try again."
    )


# ============================================================
# GET USER INFORMATION FROM FIREBASE DATABASE
# ============================================================

def get_user_data(uid, email=None):

    try:

        # Change "users" to your existing Firebase collection/path
        # if your project currently uses a different one.
        user_ref = db.reference(f"users/{uid}")

        user_data = user_ref.get()

        if user_data:

            return {
                "uid": uid,
                "email": email or user_data.get("email", ""),
                "name": user_data.get("name", "User"),
                "role": user_data.get("role", "User")
            }

        return {
            "uid": uid,
            "email": email or "",
            "name": "User",
            "role": "User"
        }

    except Exception:

        return {
            "uid": uid,
            "email": email or "",
            "name": "User",
            "role": "User"
        }


# ============================================================
# REGISTER
# ============================================================

def register():

    st.subheader("📝 Create an Account")

    name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="register_name"
    )

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email",
        key="register_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Create a password",
        key="register_password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm your password",
        key="register_confirm_password"
    )

    st.caption(
        "Your password must contain at least 6 characters."
    )

    if st.button(
        "📝 Create Account",
        use_container_width=True,
        type="primary"
    ):

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not name.strip():

            st.error("Please enter your name.")
            return

        if not email.strip():

            st.error("Please enter your email address.")
            return

        if not password:

            st.error("Please enter a password.")
            return

        if len(password) < 6:

            st.error(
                "Password must contain at least 6 characters."
            )
            return

        if password != confirm_password:

            st.error("Passwords do not match.")
            return

        # ----------------------------------------------------
        # Create Firebase Authentication account
        # ----------------------------------------------------

        try:

            response = requests.post(
                SIGN_UP_URL,
                json={
                    "email": email.strip(),
                    "password": password,
                    "returnSecureToken": True
                },
                timeout=15
            )

            data = response.json()

            if response.status_code != 200:

                error_code = (
                    data
                    .get("error", {})
                    .get("message", "UNKNOWN_ERROR")
                )

                st.error(
                    firebase_error_message(error_code)
                )

                return

            uid = data["localId"]
            id_token = data["idToken"]

            # ------------------------------------------------
            # Store additional user information
            # ------------------------------------------------

            user_data = {
                "uid": uid,
                "name": name.strip(),
                "email": email.strip(),
                "role": "User"
            }

            db.reference(
                f"users/{uid}"
            ).set(user_data)

            # ------------------------------------------------
            # Send email verification
            # ------------------------------------------------

            verify_url = (
                "https://identitytoolkit.googleapis.com/v1/"
                "accounts:sendOobCode"
                "?key=" + FIREBASE_WEB_API_KEY
            )

            verify_response = requests.post(
                verify_url,
                json={
                    "requestType": "VERIFY_EMAIL",
                    "idToken": id_token
                },
                timeout=15
            )

            if verify_response.status_code == 200:

                st.success(
                    "Account created successfully!"
                )

                st.info(
                    "📧 A verification email has been sent to "
                    + email.strip()
                    + ". Please verify your email before logging in."
                )

            else:

                st.success(
                    "Account created successfully!"
                )

                st.warning(
                    "Your account was created, but the verification "
                    "email could not be sent. You can try again later."
                )

        except requests.exceptions.RequestException:

            st.error(
                "Could not connect to Firebase. "
                "Please check your internet connection."
            )

        except Exception as e:

            st.error(
                f"Registration error: {str(e)}"
            )


# ============================================================
# LOGIN
# ============================================================

def login():

    st.subheader("🔐 Login")

    email = st.text_input(
        "Email Address",
        placeholder="Enter your email",
        key="login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password"
    )

    if st.button(
        "🔐 Login",
        use_container_width=True,
        type="primary"
    ):

        if not email.strip():

            st.error("Please enter your email address.")
            return

        if not password:

            st.error("Please enter your password.")
            return

        try:

            # ------------------------------------------------
            # Firebase email/password authentication
            # ------------------------------------------------

            response = requests.post(
                SIGN_IN_URL,
                json={
                    "email": email.strip(),
                    "password": password,
                    "returnSecureToken": True
                },
                timeout=15
            )

            data = response.json()

            if response.status_code != 200:

                error_code = (
                    data
                    .get("error", {})
                    .get("message", "UNKNOWN_ERROR")
                )

                st.error(
                    firebase_error_message(error_code)
                )

                return

            uid = data["localId"]
            id_token = data["idToken"]
            user_email = data.get(
                "email",
                email.strip()
            )

            # ------------------------------------------------
            # Check email verification
            # ------------------------------------------------

            lookup_response = requests.post(
                LOOKUP_URL,
                json={
                    "idToken": id_token
                },
                timeout=15
            )

            if lookup_response.status_code == 200:

                lookup_data = lookup_response.json()

                users = lookup_data.get("users", [])

                if users:

                    email_verified = users[0].get(
                        "emailVerified",
                        False
                    )

                    if not email_verified:

                        st.warning(
                            "📧 Please verify your email address "
                            "before logging in."
                        )

                        st.info(
                            "Check your email inbox for the Firebase "
                            "verification email."
                        )

                        return

            # ------------------------------------------------
            # Get user data from Realtime Database
            # ------------------------------------------------

            user_data = get_user_data(
                uid,
                user_email
            )

            # ------------------------------------------------
            # Session management
            # ------------------------------------------------

            st.session_state["logged_in"] = True

            st.session_state["user"] = user_data

            st.session_state["redirect_dashboard"] = True

            st.success(
                f"Welcome back, {user_data['name']}! 👋"
            )

            st.rerun()

        except requests.exceptions.RequestException:

            st.error(
                "Could not connect to Firebase. "
                "Please check your internet connection."
            )

        except Exception as e:

            st.error(
                f"Login error: {str(e)}"
            )

    # ========================================================
    # FORGOT PASSWORD
    # ========================================================

    st.markdown("---")

    if st.button(
        "🔑 Forgot Password?",
        use_container_width=True
    ):

        st.session_state["show_forgot_password"] = True

    # ========================================================
    # FORGOT PASSWORD FORM
    # ========================================================

    if st.session_state.get(
        "show_forgot_password",
        False
    ):

        st.markdown("---")

        st.subheader("🔑 Reset Your Password")

        reset_email = st.text_input(
            "Enter your email address",
            placeholder="your@email.com",
            key="reset_email"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "📧 Send Reset Email",
                use_container_width=True,
                type="primary"
            ):

                if not reset_email.strip():

                    st.error(
                        "Please enter your email address."
                    )

                else:

                    try:

                        response = requests.post(
                            PASSWORD_RESET_URL,
                            json={
                                "requestType": "PASSWORD_RESET",
                                "email": reset_email.strip()
                            },
                            timeout=15
                        )

                        data = response.json()

                        if response.status_code == 200:

                            st.success(
                                "📧 Password reset email sent!"
                            )

                            st.info(
                                "Check your email inbox and follow "
                                "the link to create a new password."
                            )

                        else:

                            error_code = (
                                data
                                .get("error", {})
                                .get(
                                    "message",
                                    "UNKNOWN_ERROR"
                                )
                            )

                            st.error(
                                firebase_error_message(
                                    error_code
                                )
                            )

                    except requests.exceptions.RequestException:

                        st.error(
                            "Could not connect to Firebase."
                        )

                    except Exception as e:

                        st.error(
                            f"Password reset error: {str(e)}"
                        )

        with col2:

            if st.button(
                "❌ Cancel",
                use_container_width=True
            ):

                st.session_state[
                    "show_forgot_password"
                ] = False

                st.rerun()