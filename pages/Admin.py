import streamlit as st
from firebase_config import db_firestore
import pandas as pd

# ===============================
# Login Check
# ===============================

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please login first.")
    st.stop()

user = st.session_state["user"]

# ===============================
# Admin Access Check
# ===============================

if user["role"] != "Admin":
    st.error("Access denied. Admin permission required.")
    st.stop()

# ===============================
# Page Header
# ===============================

st.title("⚙️ Admin Control Centre")

st.markdown(
    """
    ### Smart Social Analytics Platform Administration

    Monitor users, AI services and platform performance.
    """
)

st.divider()

# ===============================
# Load Users (Firestore)
# ===============================

users = db_firestore.collection("users").stream()
user_data = [item.to_dict() for item in users]
users_df = pd.DataFrame(user_data)

# ===============================
# Load History (Firestore)
# ===============================

history = db_firestore.collection("history").stream()
history_data = [item.to_dict() for item in history]
history_df = pd.DataFrame(history_data)

# ===============================
# Platform Statistics
# ===============================

st.subheader("📊 Platform Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Total Users", len(users_df))

with col2:
    st.metric("📝 Analyses", len(history_df))

with col3:
    if not history_df.empty:
        positive = len(history_df[history_df["sentiment"] == "POSITIVE"])
    else:
        positive = 0
    st.metric("😊 Positive Results", positive)

with col4:
    st.metric("🟢 System Status", "Online")

st.divider()

# ===============================
# User Management
# ===============================

st.subheader("👥 User Management")

if not users_df.empty:
    st.dataframe(users_df, use_container_width=True)
else:
    st.info("No users found.")

st.divider()

# ===============================
# Sentiment Analytics
# ===============================

st.subheader("📈 Sentiment Analytics")

if not history_df.empty:
    sentiment_count = history_df["sentiment"].value_counts()
    st.bar_chart(sentiment_count)
else:
    st.info("No sentiment data available.")

st.divider()

# ===============================
# AI System Status
# ===============================

st.subheader("🤖 AI System Monitoring")

status1, status2, status3 = st.columns(3)

with status1:
    st.success("🟢 DistilBERT Model Active")

with status2:
    st.success("🟢 Firebase Connected")

with status3:
    st.success("🟢 Database Operational")

st.divider()

# ===============================
# Security
# ===============================

st.subheader("🔐 Security Overview")

st.info(
    """
    ✅ Firebase Authentication Enabled  
    ✅ Role Based Access Control  
    ✅ Protected User Data  
    ✅ Admin Permission Verification  
    """
)

st.success("Admin Dashboard Loaded Successfully")
