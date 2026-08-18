import streamlit as st
import random
from datetime import datetime

from models.sentiment_model import analyse_sentiment
from firebase_config import live_posts_ref, live_sentiment_ref


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Live Social Stream",
    page_icon="🔴",
    layout="wide"
)


# =========================================================
# LOGIN CHECK
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.warning("Please login first.")
    st.stop()


user = st.session_state["user"]


# =========================================================
# SESSION STATE
# =========================================================

if "live_stream_running" not in st.session_state:
    st.session_state["live_stream_running"] = False

if "stream_count" not in st.session_state:
    st.session_state["stream_count"] = 0


# =========================================================
# DEMO SOCIAL POSTS
# =========================================================

SOCIAL_POSTS = [

    "The new smartphone camera is absolutely amazing!",

    "This update is terrible and the app keeps crashing.",

    "The company announced a new product today.",

    "I really love the new design. It looks fantastic!",

    "Customer support was very disappointing.",

    "The software update will be available next Monday.",

    "This product is one of the best things I have purchased.",

    "The battery life is horrible after the latest update.",

    "The event starts at 9 AM tomorrow morning.",

    "Really impressed with the new features!",

    "The service was slow and frustrating.",

    "The company released its quarterly report today.",

    "Amazing performance and excellent user experience.",

    "The application keeps freezing and I hate it.",

    "A new version of the application has been released.",

    "I am extremely happy with this purchase.",

    "Very poor experience. I would not recommend this.",

    "The new feature was introduced during today's presentation.",

    "The new interface is beautiful and easy to use.",

    "This is probably the worst update they have released."
]


# =========================================================
# HEADER
# =========================================================

st.title("🔴 Live Social Media Analytics")

st.markdown(
    """
    ### AI-Powered Live Social Stream

    Incoming social media posts are automatically analysed using
    **Twitter-RoBERTa Sentiment Analysis** and stored in
    **Firebase Realtime Database**.
    """
)

st.divider()


# =========================================================
# STREAM CONTROLS
# =========================================================

control1, control2, control3 = st.columns(3)


with control1:

    if st.button(
        "▶ Start Live Stream",
        use_container_width=True
    ):

        st.session_state["live_stream_running"] = True
        st.success("Live stream started.")


with control2:

    if st.button(
        "⏹ Stop Live Stream",
        use_container_width=True
    ):

        st.session_state["live_stream_running"] = False
        st.warning("Live stream stopped.")


with control3:

    if st.button(
        "🗑 Reset Local Counter",
        use_container_width=True
    ):

        st.session_state["stream_count"] = 0


st.divider()


# =========================================================
# LIVE STATUS
# =========================================================

if st.session_state["live_stream_running"]:

    st.success(
        "🔴 LIVE STREAM ACTIVE"
    )

else:

    st.info(
        "⚫ Live stream is currently stopped."
    )


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_realtime_records():

    data = live_sentiment_ref.get()

    if not data:
        return []

    records = []

    for record_id, item in data.items():

        if isinstance(item, dict):

            item["record_id"] = record_id

            records.append(item)

    return records


# =========================================================
# LIVE STREAM PROCESS
# =========================================================

@st.fragment(run_every="5s")
def live_stream_engine():

    # -----------------------------------------------------
    # GENERATE NEW LIVE POST
    # -----------------------------------------------------

    if st.session_state["live_stream_running"]:

        post = random.choice(
            SOCIAL_POSTS
        )

        timestamp = datetime.now().isoformat()


        # -------------------------------------------------
        # SAVE RAW POST
        # -------------------------------------------------

        live_posts_ref.push({

            "text": post,

            "source": "Live Stream Simulator",

            "user_id": user["uid"],

            "timestamp": timestamp

        })


        # -------------------------------------------------
        # AI SENTIMENT ANALYSIS
        # -------------------------------------------------

        result = analyse_sentiment(
            post
        )


        # -------------------------------------------------
        # SAVE SENTIMENT RESULT
        # -------------------------------------------------

        live_sentiment_ref.push({

            "text": post,

            "sentiment": result["sentiment"],

            "confidence": result["confidence"],

            "source": "Live Stream Simulator",

            "user_id": user["uid"],

            "name": user["name"],

            "timestamp": timestamp

        })


        st.session_state["stream_count"] += 1


    # =====================================================
    # READ FIREBASE DATA
    # =====================================================

    records = get_realtime_records()


    # =====================================================
    # COUNTERS
    # =====================================================

    positive = 0
    neutral = 0
    negative = 0


    for record in records:

        sentiment = record.get(
            "sentiment",
            ""
        )

        if sentiment == "POSITIVE":

            positive += 1

        elif sentiment == "NEGATIVE":

            negative += 1

        elif sentiment == "NEUTRAL":

            neutral += 1


    total = (
        positive +
        neutral +
        negative
    )


    # =====================================================
    # LIVE METRICS
    # =====================================================

    st.subheader(
        "📊 Live Analytics"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.metric(
            "Total Posts",
            total
        )


    with metric2:

        st.metric(
            "😊 Positive",
            positive
        )


    with metric3:

        st.metric(
            "😐 Neutral",
            neutral
        )


    with metric4:

        st.metric(
            "😡 Negative",
            negative
        )


    # =====================================================
    # PERCENTAGES
    # =====================================================

    if total > 0:

        positive_percentage = round(
            (positive / total) * 100,
            1
        )

        neutral_percentage = round(
            (neutral / total) * 100,
            1
        )

        negative_percentage = round(
            (negative / total) * 100,
            1
        )

    else:

        positive_percentage = 0
        neutral_percentage = 0
        negative_percentage = 0


    st.divider()


    # =====================================================
    # SENTIMENT DISTRIBUTION
    # =====================================================

    st.subheader(
        "📈 Live Sentiment Distribution"
    )


    chart_data = {

        "Positive": positive_percentage,

        "Neutral": neutral_percentage,

        "Negative": negative_percentage

    }


    st.bar_chart(
        chart_data
    )


    # =====================================================
    # CURRENT TREND
    # =====================================================

    st.subheader(
        "🔥 Current Sentiment Trend"
    )


    if total == 0:

        st.info(
            "Waiting for live data..."
        )


    elif positive > negative and positive > neutral:

        st.success(
            f"""
            📈 POSITIVE TREND

            Positive sentiment is currently dominant.

            Positive: {positive_percentage}%
            """
        )


    elif negative > positive and negative > neutral:

        st.error(
            f"""
            📉 NEGATIVE TREND

            Negative sentiment is currently dominant.

            Negative: {negative_percentage}%
            """
        )


    else:

        st.info(
            f"""
            ➡ STABLE / NEUTRAL TREND

            No single sentiment is strongly dominant.
            """
        )


    st.divider()


    # =====================================================
    # LATEST LIVE POSTS
    # =====================================================

    st.subheader(
        "📡 Latest Live Posts"
    )


    if not records:

        st.info(
            "Waiting for incoming social media posts..."
        )

        return


    # Sort newest first
    records.sort(
        key=lambda x: x.get(
            "timestamp",
            ""
        ),
        reverse=True
    )


    latest_records = records[:10]


    for record in latest_records:

        sentiment = record.get(
            "sentiment",
            "UNKNOWN"
        )

        text = record.get(
            "text",
            ""
        )

        confidence = record.get(
            "confidence",
            0
        )

        timestamp = record.get(
            "timestamp",
            ""
        )


        if sentiment == "POSITIVE":

            emoji = "😊"

        elif sentiment == "NEGATIVE":

            emoji = "😡"

        else:

            emoji = "😐"


        st.markdown(
            f"""
            **{emoji} {sentiment} — {confidence}%**

            {text}

            🕒 {timestamp}

            ---
            """
        )


# =========================================================
# START LIVE FRAGMENT
# =========================================================

live_stream_engine()