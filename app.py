import streamlit as st
from auth import login, register


# ==========================================
# Page Configuration
# ==========================================

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
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
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
# Landing Page
# ==========================================

def landing_page():

    # ======================================
    # 3D Animated Hero
    # ======================================

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

    # ======================================
    # Feature Cards
    # ======================================

    st.subheader("🌟 Intelligent Analytics Platform")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
<div class="card">
<div class="card-icon">🧠</div>
<h3>AI Sentiment Analysis</h3>
<p>
Analyse social media opinions using a three-class
RoBERTa NLP model.
</p>
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
<p>
Use machine learning to identify sentiment patterns
and forecast future audience behaviour.
</p>
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
<p>
Transform historical sentiment data into useful
visual insights for smarter decision making.
</p>
<b>Real-Time Analytics</b>
</div>
""",
            unsafe_allow_html=True
        )

    st.divider()

    # ======================================
    # Business Introduction
    # ======================================

    left, right = st.columns([1.4, 1])

    with left:
        st.markdown(
            """
## 🚀 Turn Social Conversations Into Intelligence

Smart Social Analytics helps organisations understand
public opinion, identify changing sentiment, and support
data-driven business decisions.

### Why it matters

- Understand customer opinions quickly
- Detect negative sentiment early
- Monitor audience behaviour
- Identify changing sentiment patterns
- Forecast future audience behaviour
- Support strategic decision making
"""
        )

    with right:
        st.markdown(
            """
<div class="card tech-card">
<h3>🛠️ Technology Stack</h3>
<p>🤖 RoBERTa NLP Model</p>
<p>🧠 Machine Learning</p>
<p>☁ Firebase Cloud Database</p>
<p>📡 Realtime Database</p>
<p>📊 Data Analytics</p>
<p>🔐 Firebase Authentication</p>
</div>
""",
            unsafe_allow_html=True
        )

    st.divider()

    # ======================================
    # Platform Capabilities
    # ======================================

    st.subheader("⚡ Platform Capabilities")

    status1, status2, status3, status4, status5 = st.columns(5)

    with status1:
        st.metric("🤖 AI Engine", "Active")

    with status2:
        st.metric("☁ Database", "Connected")

    with status3:
        st.metric("🔐 Security", "Enabled")

    with status4:
        st.metric("📈 Forecast", "7 Days")

    with status5:
        st.metric("🔴 Live Stream", "Ready")


# ==========================================
# Redirect After Login
# ==========================================

if st.session_state["redirect_dashboard"]:
    st.session_state["redirect_dashboard"] = False
    st.switch_page("pages/Dashboard.py")


# ==========================================
# Before Login
# ==========================================

if not st.session_state["logged_in"]:

    landing_page()

    st.sidebar.markdown(
        """
## 🔐 Account

Welcome to Smart Social Analytics.
"""
    )

    option = st.sidebar.radio(
        "Choose Option",
        [
            "Login",
            "Register"
        ]
    )

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

    st.sidebar.divider()


    # ======================================
    # Admin Panel
    # ======================================

    if user["role"] == "Admin":

        if st.sidebar.button(
            "🛡️ Admin Panel",
            use_container_width=True
        ):

            st.switch_page(
                "pages/Admin.py"
            )


    st.sidebar.success(
        "🟢 AI Platform Online"
    )


    # ======================================
    # Logout
    # ======================================

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.clear()

        st.rerun()


    # ======================================
    # Navigation
    # ======================================

    if page == "🏠 Dashboard":

        st.switch_page(
            "pages/Dashboard.py"
        )


    elif page == "🔴 Live Stream":

        st.switch_page(
            "pages/LiveStream.py"
        )


    elif page == "🤖 Sentiment":

        st.switch_page(
            "pages/Sentiment.py"
        )


    elif page == "📈 Trend Prediction":

        st.switch_page(
            "pages/TrendPrediction.py"
        )


    elif page == "📜 History":

        st.switch_page(
            "pages/History.py"
        )


    elif page == "👤 Profile":

        st.switch_page(
            "pages/Profile.py"
        )


    elif page == "⚙️ Settings":

        st.switch_page(
            "pages/Settings.py"
        )


# ==========================================
# Footer
# ==========================================

st.markdown(
    """
<div class="footer">

<strong>
📊 Smart Social Analytics Platform
</strong>

<br><br>

AI • Machine Learning • Realtime Analytics • Data Intelligence

<br>

Powered by RoBERTa NLP, Firebase and Machine Learning

<br><br>

Developed by Debug Dynamos | ICT Project 2026

</div>
""",
    unsafe_allow_html=True
)