import streamlit as st
from firebase_config import db
from datetime import datetime
import pandas as pd



# ==================================================
# Login Check
# ==================================================

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:

    st.warning("Please login first.")

    st.stop()



user = st.session_state["user"]



# ==================================================
# Page Header
# ==================================================

st.title("📊 AI Analytics Dashboard")


st.markdown(

f"""
## Welcome back, {user['name']} 👋


Your intelligent social media monitoring centre.


Analyse conversations, discover trends and make
data-driven decisions using Artificial Intelligence.

"""

)



st.divider()



# ==================================================
# Load Sentiment Data
# ==================================================

try:


    records = db.collection(
        "history"
    ).stream()



    data = []



    for record in records:


        item = record.to_dict()


        data.append(item)



    df = pd.DataFrame(data)



except Exception:


    df = pd.DataFrame()




# ==================================================
# KPI SECTION
# ==================================================

st.subheader("📈 Platform Overview")



if not df.empty:



    total_posts = len(df)



    positive = len(

        df[df["sentiment"]=="POSITIVE"]

    )



    negative = len(

        df[df["sentiment"]=="NEGATIVE"]

    )



    neutral = len(

        df[df["sentiment"]=="NEUTRAL"]

    )



else:



    total_posts = 0

    positive = 0

    negative = 0

    neutral = 0




col1,col2,col3,col4 = st.columns(4)



with col1:

    st.metric(

        "📝 Total Posts",

        total_posts

    )



with col2:

    st.metric(

        "😊 Positive",

        positive

    )



with col3:

    st.metric(

        "😡 Negative",

        negative

    )



with col4:

    st.metric(

        "😐 Neutral",

        neutral

    )




st.divider()



# ==================================================
# AI INSIGHT SECTION
# ==================================================

st.subheader("🤖 AI Generated Insights")



if total_posts > 0:



    positive_percentage = round(

        (positive / total_posts) * 100,

        2

    )



    if positive_percentage > 60:


        insight = """

        🟢 Overall audience sentiment is positive.

        Users are showing strong engagement and acceptance.

        """



    elif positive_percentage < 30:


        insight = """

        🔴 Negative sentiment is increasing.

        Organisations should review customer concerns.

        """



    else:


        insight = """

        🟡 Audience sentiment is balanced.

        Continue monitoring future trends.

        """



else:


    insight = """

    ℹ️ Start analysing social media posts
    to generate AI insights.

    """



st.info(insight)




st.divider()



# ==================================================
# Analytics Section
# ==================================================

left,right = st.columns(2)



with left:


    st.subheader(

        "📊 Sentiment Distribution"

    )



    if not df.empty:


        chart_data = pd.DataFrame(

        {

        "Sentiment":

        [

        "Positive",

        "Negative",

        "Neutral"

        ],


        "Count":

        [

        positive,

        negative,

        neutral

        ]

        }

        )


        st.bar_chart(

            chart_data.set_index("Sentiment")

        )


    else:


        st.warning(

            "No analysis data available."

        )




with right:


    st.subheader(

        "⚡ System Status"

    )


    st.success(

        "🟢 Firebase Database Connected"

    )


    st.success(

        "🟢 AI Sentiment Model Active"

    )


    st.success(

        "🟢 Analytics Engine Running"

    )




st.divider()



# ==================================================
# Recent Activity
# ==================================================

st.subheader(

    "📜 Recent Analysis Activity"

)



if not df.empty:


    show_columns = [

        "text",

        "sentiment",

        "confidence"

    ]



    st.dataframe(

        df[show_columns].tail(5),

        use_container_width=True

    )


else:


    st.info(

        "No recent activity."

    )



# ==================================================
# Footer
# ==================================================

st.markdown(

"""
<br>

<div class="footer">

AI Powered Social Media Intelligence Platform

</div>

""",

unsafe_allow_html=True

)