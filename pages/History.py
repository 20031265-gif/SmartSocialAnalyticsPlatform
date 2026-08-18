import streamlit as st
from firebase_config import db
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

st.title("📜 Sentiment Analytics Reports")


st.markdown(

f"""
### Analysis history for {user['name']}

Review previous AI sentiment predictions and
understand audience behaviour.

"""

)



st.divider()



# ==================================================
# Load Data From Firestore
# ==================================================

records = db.collection(
    "history"
).stream()



data = []



for record in records:


    item = record.to_dict()


    # show only current user data

    if item.get("user_id") == user["uid"]:

        data.append(item)



df = pd.DataFrame(data)



# ==================================================
# Empty Check
# ==================================================

if df.empty:


    st.info(

        "No sentiment analysis records found."

    )


    st.stop()




# ==================================================
# Summary Cards
# ==================================================

st.subheader(

    "📊 Analytics Summary"

)



total = len(df)



positive = len(

    df[df["sentiment"]=="POSITIVE"]

)



negative = len(

    df[df["sentiment"]=="NEGATIVE"]

)



neutral = len(

    df[df["sentiment"]=="NEUTRAL"]

)



col1,col2,col3,col4 = st.columns(4)



with col1:


    st.metric(

        "Total Posts",

        total

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
# Chart Section
# ==================================================

left,right = st.columns(2)



with left:


    st.subheader(

        "📈 Sentiment Distribution"

    )


    chart = pd.DataFrame(

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

        chart.set_index("Sentiment")

    )




with right:


    st.subheader(

        "🤖 AI Performance"

    )


    avg_confidence = round(

        df["confidence"].mean(),

        2

    )



    st.metric(

        "Average AI Confidence",

        f"{avg_confidence}%"

    )


    st.success(

        "DistilBERT Sentiment Model Active"

    )




st.divider()



# ==================================================
# Filter
# ==================================================

st.subheader(

    "🔍 Filter Reports"

)



filter_option = st.selectbox(

    "Select Sentiment",

    [

        "All",

        "POSITIVE",

        "NEGATIVE",

        "NEUTRAL"

    ]

)



filtered_df = df.copy()



if filter_option != "All":


    filtered_df = filtered_df[

        filtered_df["sentiment"]

        ==

        filter_option

    ]




# ==================================================
# Display Records
# ==================================================

st.subheader(

    "📋 Analysis Records"

)



display_columns = [

    "text",

    "sentiment",

    "confidence",

    "created_at"

]



st.dataframe(

    filtered_df[display_columns],

    use_container_width=True

)



st.success(

    f"Showing {len(filtered_df)} analysis records"

)



# ==================================================
# Footer
# ==================================================

st.markdown(

"""
<br>

<div class="footer">

Smart Social Analytics Reporting System

</div>

""",

unsafe_allow_html=True

)