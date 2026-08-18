import streamlit as st
from models.sentiment_model import analyse_sentiment
from firebase_config import db, live_sentiment_ref
from datetime import datetime


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="AI Sentiment Analysis",
    page_icon="😊",
    layout="wide"
)


# -----------------------------
# Login Check
# -----------------------------

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please login first.")
    st.stop()


user = st.session_state["user"]


# -----------------------------
# Header
# -----------------------------

st.title("😊 AI Sentiment Analysis")

st.markdown(
"""
### Understand social media emotions using Artificial Intelligence

The platform uses the **Twitter-RoBERTa NLP model**
to classify social media text into:

😊 Positive  
😐 Neutral  
😡 Negative
"""
)

st.divider()


# -----------------------------
# Example Section
# -----------------------------

st.subheader("💡 Try Example Text")

example_col1, example_col2, example_col3 = st.columns(3)


with example_col1:

    if st.button("😊 Positive Example"):
        st.session_state.example = (
            "I love this application. "
            "It is amazing and very useful."
        )


with example_col2:

    if st.button("😡 Negative Example"):
        st.session_state.example = (
            "This application is terrible "
            "and very slow."
        )


with example_col3:

    if st.button("😐 Neutral Example"):
        st.session_state.example = (
            "The university announced "
            "a new event today."
        )


# -----------------------------
# Input Area
# -----------------------------

st.subheader("📝 Enter Social Media Text")

default_text = st.session_state.get(
    "example",
    ""
)

text = st.text_area(
    "Post Content",
    value=default_text,
    height=150,
    placeholder="Write or paste social media content here..."
)


# -----------------------------
# Analyse Button
# -----------------------------

if st.button(
    "🚀 Analyse with AI",
    use_container_width=True
):

    if text.strip() == "":

        st.warning(
            "Please enter text first."
        )

    else:

        try:

            with st.spinner(
                "AI is analysing sentiment..."
            ):

                result = analyse_sentiment(
                    text
                )

            st.success(
                "Analysis completed successfully!"
            )

            st.divider()


            # -----------------------------
            # Result Display
            # -----------------------------

            st.subheader(
                "🤖 AI Analysis Result"
            )

            col1, col2 = st.columns(2)


            with col1:

                sentiment = result["sentiment"]

                if sentiment == "POSITIVE":

                    st.success(
                        """
                        😊 POSITIVE

                        The text shows positive emotion.
                        """
                    )

                elif sentiment == "NEGATIVE":

                    st.error(
                        """
                        😡 NEGATIVE

                        The text shows negative emotion.
                        """
                    )

                else:

                    st.info(
                        """
                        😐 NEUTRAL

                        The text shows a balanced or neutral emotion.
                        """
                    )


            with col2:

                confidence = result["confidence"]

                st.metric(
                    "AI Confidence",
                    f"{confidence}%"
                )

                st.progress(
                    int(confidence)
                )


            st.divider()


            # -----------------------------
            # AI Explanation
            # -----------------------------

            st.subheader(
                "💡 AI Interpretation"
            )

            if sentiment == "POSITIVE":

                st.write(
                    """
                    The analysed content indicates
                    positive opinion, satisfaction,
                    or favourable feedback.
                    """
                )

            elif sentiment == "NEGATIVE":

                st.write(
                    """
                    The analysed content indicates
                    dissatisfaction, criticism,
                    or negative feedback.
                    """
                )

            else:

                st.write(
                    """
                    The analysed content contains
                    neutral information without
                    strong positive or negative emotion.
                    """
                )


            st.divider()


            # -----------------------------
            # Save to Firestore History
            # -----------------------------

            db.collection("history").add({

                "user_id": user["uid"],

                "name": user["name"],

                "text": text,

                "sentiment": result["sentiment"],

                "confidence": result["confidence"],

                "created_at": datetime.now()

            })


            # -----------------------------
            # Save to Realtime Database
            # -----------------------------

            live_sentiment_ref.push({

                "user_id": user["uid"],

                "name": user["name"],

                "text": text,

                "sentiment": result["sentiment"],

                "confidence": result["confidence"],

                "timestamp": datetime.now().isoformat()

            })


            st.success(
                "📌 Analysis saved to history and live database."
            )


        except Exception as e:

            st.error(
                "Something went wrong during sentiment analysis."
            )

            st.write(e)


# -----------------------------
# Model Information
# -----------------------------

st.divider()

st.subheader(
    "🤖 AI Model Information"
)

st.info(
"""
Model:
CardiffNLP Twitter-RoBERTa Sentiment Model

Technology:
Natural Language Processing (NLP)

Purpose:
Analyse sentiment from social media text.

Output:
Positive / Neutral / Negative sentiment with confidence score.
"""
)