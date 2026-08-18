import streamlit as st
import pyrebase

from firebase_config import db
from datetime import datetime



# ==================================================
# Firebase Configuration
# ==================================================

firebaseConfig = {

    "apiKey": "AIzaSyBfXbYCsa_deF1l4vJ8ZLsrySIOVTIJOys",

    "authDomain": "smartsocialanalyticsplatform.firebaseapp.com",

    "projectId": "smartsocialanalyticsplatform",

    "storageBucket": "smartsocialanalyticsplatform.firebasestorage.app",

    "messagingSenderId": "133288767996",

    "appId": "1:133288767996:web:b93160f083eab4b54f0279",

    "databaseURL":
    "https://smartsocialanalyticsplatform-default-rtdb.firebaseio.com/"

}



# Initialize Firebase

firebase = pyrebase.initialize_app(firebaseConfig)


auth = firebase.auth()



# ==================================================
# LOGIN FUNCTION
# ==================================================

def login():


    st.subheader(
        "🔐 Welcome Back"
    )


    st.markdown(
    """
    ### Smart Social Analytics Platform

    Login to access your AI-powered dashboard.

    Features:

    ✅ Sentiment Analysis

    ✅ Trend Prediction

    ✅ Analytics Reports

    ✅ Business Insights
    """
    )


    st.divider()



    with st.form(
        "login_form"
    ):


        email = st.text_input(

            "📧 Email Address"

        )


        password = st.text_input(

            "🔑 Password",

            type="password"

        )


        submit = st.form_submit_button(

            "🚀 Login",

            use_container_width=True

        )



    if submit:


        if not email or not password:


            st.warning(

                "Please enter email and password."

            )

            return



        try:


            user = auth.sign_in_with_email_and_password(

                email.strip(),

                password

            )



            user_id = user["localId"]



            user_doc = db.collection(
                "users"
            ).document(
                user_id
            ).get()



            if user_doc.exists:


                user_data = user_doc.to_dict()



                # Create session


                st.session_state["logged_in"] = True



                st.session_state["user"] = {


                    "uid": user_id,


                    "name": user_data["name"],


                    "email": user_data["email"],


                    "role": user_data["role"]


                }



                st.session_state[
                    "redirect_dashboard"
                ] = True



                st.success(

                    f"Welcome {user_data['name']} 👋"

                )



                st.rerun()



            else:


                st.error(

                    "User profile not found."

                )



        except Exception as e:



            st.error(

                "Invalid email or password."

            )



# ==================================================
# REGISTER FUNCTION
# ==================================================

def register():


    st.subheader(

        "📝 Create Your Account"

    )



    st.markdown(

    """
    Join Smart Social Analytics Platform

    Get access to:

    🤖 AI Sentiment Detection

    📈 Trend Forecasting

    📊 Analytics Dashboard

    🔥 Smart Business Insights

    """

    )



    st.divider()



    with st.form(

        "register_form"

    ):


        name = st.text_input(

            "👤 Full Name"

        )


        email = st.text_input(

            "📧 Email Address"

        )


        password = st.text_input(

            "🔑 Password",

            type="password"

        )



        role = st.selectbox(

            "Account Role",

            [

                "User",

                "Admin"

            ]

        )



        submit = st.form_submit_button(

            "Create Account",

            use_container_width=True

        )



    if submit:



        if not name or not email or not password:


            st.warning(

                "Please complete all fields."

            )

            return



        try:



            # Create Firebase account


            user = auth.create_user_with_email_and_password(

                email.strip(),

                password

            )



            user_id = user["localId"]




            # Save Firestore profile


            db.collection(

                "users"

            ).document(

                user_id

            ).set(

            {


                "name": name,


                "email": email.strip(),


                "role": role,


                "created_at": datetime.now()


            }

            )



            st.success(

                "🎉 Account created successfully!"

            )


            st.info(

                "Please login using your new account."

            )



        except Exception as e:



            error = str(e)



            if "EMAIL_EXISTS" in error:


                st.error(

                    "This email is already registered."

                )


            elif "INVALID_EMAIL" in error:


                st.error(

                    "Please enter a valid email."

                )


            else:


                st.error(

                    "Registration failed."

                )

                st.write(error)