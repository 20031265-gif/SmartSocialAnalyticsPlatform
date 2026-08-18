import streamlit as st


# =========================================================
# LOGIN CHECK
# =========================================================

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please login to access Settings.")
    st.stop()


user = st.session_state["user"]


# =========================================================
# PAGE HEADER
# =========================================================

st.title("⚙️ Settings")

st.write(
    "Manage your account preferences and platform experience."
)

st.divider()


# =========================================================
# ACCOUNT INFORMATION
# =========================================================

st.subheader("👤 Account Information")

col1, col2 = st.columns(2)

with col1:
    st.text_input(
        "Full Name",
        value=user.get("name", ""),
        disabled=True
    )

with col2:
    st.text_input(
        "Email Address",
        value=user.get("email", ""),
        disabled=True
    )


col3, col4 = st.columns(2)

with col3:
    st.text_input(
        "Account Role",
        value=user.get("role", "User"),
        disabled=True
    )

with col4:
    st.text_input(
        "Account Status",
        value="Active",
        disabled=True
    )


st.caption(
    "Account details are managed through your registered profile."
)

st.divider()


# =========================================================
# NOTIFICATION PREFERENCES
# =========================================================

st.subheader("🔔 Notification Preferences")

st.write(
    "Choose which platform notifications you would like to receive."
)


if "email_notifications" not in st.session_state:
    st.session_state["email_notifications"] = True

if "trend_notifications" not in st.session_state:
    st.session_state["trend_notifications"] = True

if "negative_alerts" not in st.session_state:
    st.session_state["negative_alerts"] = False


email_notifications = st.toggle(
    "Email notifications",
    value=st.session_state["email_notifications"]
)

trend_notifications = st.toggle(
    "Trend prediction alerts",
    value=st.session_state["trend_notifications"]
)

negative_alerts = st.toggle(
    "Negative sentiment alerts",
    value=st.session_state["negative_alerts"]
)


st.session_state["email_notifications"] = email_notifications
st.session_state["trend_notifications"] = trend_notifications
st.session_state["negative_alerts"] = negative_alerts


st.caption(
    "These preferences currently apply to your active session."
)

st.divider()


# =========================================================
# DASHBOARD PREFERENCES
# =========================================================

st.subheader("📊 Dashboard Preferences")


dashboard_view = st.selectbox(
    "Default Dashboard View",
    [
        "Overview",
        "Sentiment Analytics",
        "Trend Forecast",
        "Recent Activity"
    ]
)


report_size = st.selectbox(
    "Records Displayed in Reports",
    [
        "10 records",
        "25 records",
        "50 records",
        "100 records"
    ]
)


st.divider()


# =========================================================
# AI CONFIGURATION
# =========================================================

st.subheader("🤖 AI Configuration")

st.write(
    "Current artificial intelligence services used by the platform."
)


col1, col2 = st.columns(2)

with col1:

    st.info(
        """
        **Sentiment Model**

        DistilBERT

        Status: Active 🟢
        """
    )


with col2:

    st.info(
        """
        **Trend Engine**

        Machine Learning Forecast

        Status: Active 🟢
        """
    )


st.caption(
    "AI models are configured by the platform administrator."
)

st.divider()


# =========================================================
# SECURITY
# =========================================================

st.subheader("🔐 Security & Access")


security1, security2, security3 = st.columns(3)


with security1:
    st.success(
        """
        **Authentication**

        🟢 Enabled
        """
    )


with security2:
    st.success(
        """
        **Database**

        🟢 Connected
        """
    )


with security3:
    st.success(
        f"""
        **Access Level**

        🟢 {user.get("role", "User")}
        """
    )


st.divider()


# =========================================================
# SAVE SETTINGS
# =========================================================

st.subheader("💾 Save Preferences")


if st.button(
    "Save Settings",
    type="primary",
    use_container_width=True
):

    st.session_state["dashboard_view"] = dashboard_view
    st.session_state["report_size"] = report_size

    st.success(
        "✅ Your preferences have been saved for this session."
    )


st.divider()


# =========================================================
# ACCOUNT ACTIONS
# =========================================================

st.subheader("🚪 Account Actions")

st.write(
    "Sign out securely when you have finished using the platform."
)


if st.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.clear()

    st.rerun()