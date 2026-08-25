import streamlit as st
import pandas as pd
import time
from datetime import datetime

from models.sentiment_model import analyse_sentiment
from firebase_config import db_firestore

st.set_page_config(
    page_title="AI Sentiment Analysis",
    page_icon="😊",
    layout="wide",
)

# LOGIN CHECK
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please login first.")
    st.stop()

user = st.session_state["user"]

# SAVE RESULT FUNCTION
def save_analysis(text, result, source):
    db_firestore.collection("history").add(
        {
            "user_id": user["uid"],
            "name": user.get("name", "User"),
            "text": text,
            "sentiment": result["sentiment"],
            "confidence": result["confidence"],
            "source": source,
            "created_at": datetime.now(),
        }
    )

# HEADER
st.title("😊 AI Sentiment Analysis")
st.markdown(
    """
    ### Intelligent Social Media Sentiment Monitoring

    Analyse individual posts, batch datasets and live incoming
    social media content using the **Twitter-RoBERTa NLP model**.
    """
)
st.divider()

manual_tab, batch_tab, live_tab, analytics_tab = st.tabs(
    ["✍️ Manual Analysis", "📂 Batch Dataset", "🔴 Live Feed", "📊 Analytics"]
)

# TAB 1 - MANUAL
with manual_tab:
    st.subheader("📝 Analyse Individual Social Media Post")

    example_col1, example_col2, example_col3 = st.columns(3)

    with example_col1:
        if st.button("😊 Positive Example", key="positive_example"):
            st.session_state.example_text = (
                "I absolutely love the new update. Everything works perfectly!"
            )

    with example_col2:
        if st.button("😡 Negative Example", key="negative_example"):
            st.session_state.example_text = (
                "This app keeps crashing and the customer support is terrible."
            )

    with example_col3:
        if st.button("😐 Neutral Example", key="neutral_example"):
            st.session_state.example_text = (
                "The new version of the application was released today."
            )

    text = st.text_area(
        "Post Content",
        value=st.session_state.get("example_text", ""),
        height=150,
        placeholder="Write or paste social media content here...",
    )

    if st.button("🚀 Analyse with AI", use_container_width=True, key="analyse_manual"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            try:
                with st.spinner("AI is analysing sentiment..."):
                    result = analyse_sentiment(text)

                sentiment = result["sentiment"]
                confidence = result["confidence"]

                st.success("Analysis completed successfully!")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Sentiment", sentiment)

                with col2:
                    st.metric("Confidence", f"{confidence}%")

                with col3:
                    if confidence >= 90:
                        reliability = "Very High"
                    elif confidence >= 75:
                        reliability = "High"
                    elif confidence >= 60:
                        reliability = "Moderate"
                    else:
                        reliability = "Low"

                    st.metric("Prediction Reliability", reliability)

                st.progress(min(int(confidence), 100))

                if sentiment == "POSITIVE":
                    st.success(
                        """
                        😊 Positive sentiment detected.

                        The content contains favourable,
                        satisfied or enthusiastic language.
                        """
                    )
                elif sentiment == "NEGATIVE":
                    st.error(
                        """
                        😡 Negative sentiment detected.

                        The content contains dissatisfaction,
                        criticism or unfavourable opinion.
                        """
                    )
                else:
                    st.info(
                        """
                        😐 Neutral sentiment detected.

                        The content does not contain strong
                        positive or negative emotion.
                        """
                    )

                save_analysis(text, result, "Manual")
                st.success("📌 Result saved successfully.")

            except Exception as e:
                st.error("Sentiment analysis failed.")
                st.exception(e)

# TAB 2 - BATCH
with batch_tab:
    st.subheader("📂 Batch Social Media Analysis")
    st.write(
        """
        Upload a CSV containing multiple social media posts.

        Suitable column names include:

        `text`, `tweet`, `post`, `content`, or `message`.
        """
    )

    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"], key="batch_csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Dataset loaded: {len(df)} records")
            st.dataframe(df.head(10), use_container_width=True)

            text_column = st.selectbox("Select text column", df.columns)

            maximum = min(len(df), 500)
            number_posts = st.slider(
                "Number of posts to analyse",
                min_value=1,
                max_value=maximum,
                value=min(50, maximum),
            )

            if st.button("🤖 Analyse Dataset", use_container_width=True):
                selected_df = df.head(number_posts)
                results = []
                progress = st.progress(0)
                status = st.empty()

                for position, (_, row) in enumerate(selected_df.iterrows()):
                    post = str(row[text_column]).strip()
                    if not post or post.lower() == "nan":
                        continue

                    status.write(
                        f"Analysing post {position + 1} of {len(selected_df)}"
                    )

                    try:
                        result = analyse_sentiment(post)
                        results.append(
                            {
                                "Text": post,
                                "Sentiment": result["sentiment"],
                                "Confidence": result["confidence"],
                            }
                        )
                        save_analysis(post, result, "CSV Dataset")
                    except Exception:
                        results.append(
                            {"Text": post, "Sentiment": "ERROR", "Confidence": 0}
                        )

                    percentage = int((position + 1) / len(selected_df) * 100)
                    progress.progress(percentage)

                status.empty()
                result_df = pd.DataFrame(results)

                if len(result_df) > 0:
                    st.success(f"{len(result_df)} posts analysed.")

                    positive = (result_df["Sentiment"] == "POSITIVE").sum()
                    neutral = (result_df["Sentiment"] == "NEUTRAL").sum()
                    negative = (result_df["Sentiment"] == "NEGATIVE").sum()

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric("Total", len(result_df))
                    col2.metric("😊 Positive", positive)
                    col3.metric("😐 Neutral", neutral)
                    col4.metric("😡 Negative", negative)

                    summary_df = pd.DataFrame(
                        {
                            "Sentiment": ["Positive", "Neutral", "Negative"],
                            "Posts": [positive, neutral, negative],
                        }
                    )

                    st.subheader("📊 Sentiment Distribution")
                    st.bar_chart(summary_df.set_index("Sentiment"))

                    st.subheader("📋 Analysed Posts")
                    st.dataframe(result_df, use_container_width=True)

                    csv = result_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download Results",
                        data=csv,
                        file_name="sentiment_results.csv",
                        mime="text/csv",
                    )

        except Exception as e:
            st.error("Unable to process dataset.")
            st.exception(e)

# TAB 3 - LIVE (using recent history instead of realtime)
with live_tab:
    st.subheader("🔴 Live Social Media Monitoring")

    st.info(
        """
        This section shows the most recent sentiment analyses
        stored in Firestore.

        When posts are analysed from any source, their results
        can appear here.
        """
    )

    auto_refresh = st.toggle("Enable Live Monitoring", value=False)
    refresh_seconds = st.select_slider(
        "Refresh interval", options=[2, 5, 10, 15, 30], value=5
    )

    live_container = st.container()

    try:
        docs = (
            db_firestore.collection("history")
            .order_by("created_at", direction="DESCENDING")
            .limit(20)
            .stream()
        )

        live_posts = [doc.to_dict() for doc in docs]

        if live_posts:
            with live_container:
                st.metric("Live Records", len(live_posts))

                for post in live_posts:
                    sentiment = post.get("sentiment", "UNKNOWN")
                    confidence = post.get("confidence", 0)
                    source = post.get("source", "Unknown")

                    st.markdown("---")

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.write(post.get("text", ""))
                        st.caption(
                            f"Source: {source} | {post.get('created_at', '')}"
                        )

                    with col2:
                        if sentiment == "POSITIVE":
                            st.success(f"😊 {sentiment}")
                        elif sentiment == "NEGATIVE":
                            st.error(f"😡 {sentiment}")
                        else:
                            st.info(f"😐 {sentiment}")

                        st.write(f"{confidence}%")
        else:
            st.info("No live sentiment records available.")

    except Exception as e:
        st.error("Unable to load live sentiment data.")
        st.exception(e)

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()

# TAB 4 - ANALYTICS
with analytics_tab:
    st.subheader("📊 Sentiment Intelligence Dashboard")

    try:
        records = []
        docs = (
            db_firestore.collection("history")
            .where("user_id", "==", user["uid"])
            .stream()
        )

        for doc in docs:
            records.append(doc.to_dict())

        if not records:
            st.info("No sentiment history available yet.")
        else:
            analytics_df = pd.DataFrame(records)

            total = len(analytics_df)
            positive = (analytics_df["sentiment"] == "POSITIVE").sum()
            neutral = (analytics_df["sentiment"] == "NEUTRAL").sum()
            negative = (analytics_df["sentiment"] == "NEGATIVE").sum()
            average_confidence = (
                analytics_df["confidence"].astype(float).mean()
            )

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Total Analysed", total)
            col2.metric("😊 Positive", positive)
            col3.metric("😐 Neutral", neutral)
            col4.metric("😡 Negative", negative)
            col5.metric("Avg Confidence", f"{average_confidence:.1f}%")

            st.divider()

            distribution = pd.DataFrame(
                {
                    "Sentiment": ["Positive", "Neutral", "Negative"],
                    "Count": [positive, neutral, negative],
                }
            )

            st.subheader("📊 Overall Sentiment Distribution")
            st.bar_chart(distribution.set_index("Sentiment"))

            st.subheader("🕒 Recent Analysis")

            display_columns = [
                col
                for col in [
                    "text",
                    "sentiment",
                    "confidence",
                    "source",
                    "created_at",
                ]
                if col in analytics_df.columns
            ]

            st.dataframe(
                analytics_df[display_columns].tail(20),
                use_container_width=True,
            )

    except Exception as e:
        st.error("Unable to load analytics.")
        st.exception(e)

st.divider()
st.subheader("🤖 AI Model Information")
st.info(
    """
    **Model:** CardiffNLP Twitter-RoBERTa Sentiment Model

    **Technology:** Natural Language Processing (NLP)

    **Capabilities:**

    - Individual sentiment analysis
    - Batch social media analysis
    - Firestore sentiment history
    - Historical analytics
    - Confidence scoring
    - Positive / Neutral / Negative classification

    **Storage:**

    - Firestore for analysis history
    """
)
