import streamlit as st


# -----------------------------
# Check Login
# -----------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.stop()


# -----------------------------
# Profile Page
# -----------------------------

user = st.session_state.user


st.title("👤 My Profile")


st.success(
    f"Welcome {user['name']}"
)


st.divider()


# Display User Information

st.subheader("Account Information")


col1, col2 = st.columns(2)


with col1:

    st.write("### Name")
    st.write(user["name"])

    st.write("### Email")
    st.write(user["email"])


with col2:

    st.write("### Role")
    st.write(user["role"])

    st.write("### Account Status")
    st.write("Active")


st.divider()


st.subheader("🔐 Security")

st.write(
    "Your account is protected using Firebase Authentication."
)

st.write(
    "Role-based access control is enabled."
)