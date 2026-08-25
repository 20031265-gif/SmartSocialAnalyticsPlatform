import streamlit as st
from auth import login, register

st.set_page_config(
    page_title="Smart Social Analytics",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# Load CSS
# ==========================================

def load_css():
    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("style.css not found inside assets folder.")

load_css()

# ==========================================
# Session Management
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "redirect_dashboard" not in st.session_state:
    st.session_state["redirect_dashboard"] = False


# ==========================================
# Redirect After Login
# ==========================================

if st.session_state["redirect_dashboard"]:
    st.session_state["redirect_dashboard"] = False
    st.switch_page("pages/Dashboard.py")


# ==========================================
# Landing Page (Your animations stay)
# ==========================================

def landing_page():
    st.markdown(
        """
        <div class="hero-section">
        <h1 class="three-d-title">
        <span class="title-icon">📊</span>
        <span class="word word-1">Smart</span>
        <span class="word word-2">Social</span>
        <span class="word word-3">Analytics</span>
        </h1>

        <h3 class="three-d-subtitle">
        <span class="subtitle-word subtitle-1">AI-Powered</span>
        <span class="subtitle-word subtitle-2">Social Media</span>
        <span class="subtitle-word subtitle-3">Intelligence Platform</span>
        <span class="ai-floating">🤖</span>
        </h3>

        <div class="motion-tagline">
        <span>Analyse</span>
        <span>•</span>
        <span>Understand</span>
        <span>•</span>
        <span>Predict</span>
        </div>

        <div class="ai-3d-wrapper">
        <div class="ai-3d-cube">
        <div class="cube-face front">🤖</div>
        <div class="cube-face back">📊</div>
        <div class="cube-face right">📈</div>
        <div class="cube-face left">🧠</div>
        <div class="cube-face top">AI</div>
        <div class="cube-face bottom">☁</div>
        </div>
        </div>

        <p class="platform-status">
        <span class="status-dot"></span>
        AI Platform Online
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("🌟 Intelligent Analytics Platform")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
            <div class="card-icon">🧠</div>
            <h3>AI Sentiment Analysis</h3>
            <p>Analyse social media opinions using a three-class RoBERTa NLP model.</p>
            <b>Positive • Neutral • Negative</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
            <div class="card-icon">📈</div>
            <h3>Trend Prediction</h3>
            <p>Use machine learning to identify sentiment patterns and forecast future audience behaviour.</p>
            <b>7-Day AI Forecast</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
            <div class="card-icon">📊</div>
            <h3>Analytics Dashboard</h3>
            <p>Transform historical sentiment data into useful visual insights for smarter decision making.</p>
            <b>Real-Time Analytics</b>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================
# Before Login
# ==========================================

if not st.session_state["logged_in"]:

    landing_page()

    st.sidebar.markdown("## 🔐 Account")

    option = st.sidebar.radio("Choose Option", ["Login", "Register"])

    st.divider()

    if option == "Login":
        login()
    else:
        register()


# ==========================================
# After Login
# ==========================================

else:
    user = st.session_state["user"]

    st.sidebar.markdown(
        f"""
        ## 📊 Smart Analytics
        ---
        ### 👤 {user['name']}
        **Role:** {user['role']}
        🟢 **Active**
        """
    )

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🔴 Live Stream",
            "🤖 Sentiment",
            "📈 Trend Prediction",
            "📜 History",
            "👤 Profile",
            "⚙️ Settings"
        ]
    )

    if page == "🏠 Dashboard":
        st.switch_page("pages/Dashboard.py")
    elif page == "🔴 Live Stream":
        st.switch_page("pages/LiveStream.py")
    elif page == "🤖 Sentiment":
        st.switch_page("pages/Sentiment.py")
    elif page == "📈 Trend Prediction":
        st.switch_page("pages/TrendPrediction.py")
    elif page == "📜 History":
        st.switch_page("pages/History.py")
    elif page == "👤 Profile":
        st.switch_page("pages/Profile.py")
    elif page == "⚙️ Settings":
        st.switch_page("pages/Settings.py")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
