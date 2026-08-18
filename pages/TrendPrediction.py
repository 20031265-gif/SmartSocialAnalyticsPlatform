import streamlit as st
from firebase_config import db
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression



# ==================================================
# Login Check
# ==================================================

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:

    st.warning("Please login first.")

    st.stop()



user = st.session_state["user"]



# ==================================================
# Header
# ==================================================

st.title("📈 AI Trend Prediction Dashboard")


st.markdown(

"""
### Predict future social media sentiment behaviour using Artificial Intelligence

The system analyses historical sentiment patterns
and forecasts future audience reactions.

"""

)



st.divider()



# ==================================================
# Load Firestore History
# ==================================================

records = db.collection("history").stream()



data = []



for record in records:


    item = record.to_dict()



    if item.get("user_id") == user["uid"]:

        data.append(item)




df = pd.DataFrame(data)



if df.empty:


    st.info(

        "No sentiment data available. Analyse posts first."

    )

    st.stop()



# ==================================================
# Convert Sentiment To Score
# ==================================================

sentiment_score = {


    "POSITIVE": 1,


    "NEUTRAL": 0,


    "NEGATIVE": -1

}



df["score"] = df["sentiment"].map(sentiment_score)



df = df.reset_index()



df["index"] = df.index




# ==================================================
# AI Prediction Model
# ==================================================

X = df[["index"]]


y = df["score"]



# Remove missing values

clean = pd.concat([X,y],axis=1).dropna()



X = clean[["index"]]

y = clean["score"]




model = LinearRegression()



model.fit(

    X,

    y

)



# Future days

future_days = 7



future_index = np.arange(

    len(df),

    len(df)+future_days

).reshape(-1,1)



prediction = model.predict(

    future_index

)




# ==================================================
# Forecast Summary
# ==================================================

average_prediction = prediction.mean()



if average_prediction > 0.3:


    trend = "Positive 😊"


    recommendation = """

    Audience sentiment is improving.

    Continue current engagement strategies.

    """



elif average_prediction < -0.3:


    trend = "Negative 😡"


    recommendation = """

    Negative reactions are increasing.

    Review customer concerns and feedback.

    """



else:


    trend = "Stable 😐"


    recommendation = """

    Audience sentiment is stable.

    Continue monitoring future changes.

    """




# ==================================================
# KPI Cards
# ==================================================

st.subheader("📊 AI Forecast Overview")



col1,col2,col3 = st.columns(3)



with col1:


    st.metric(

        "Current Trend",

        trend

    )



with col2:


    st.metric(

        "Prediction Period",

        "7 Days"

    )



with col3:


    confidence = round(

        max(abs(prediction))*100,

        2

    )


    st.metric(

        "AI Confidence",

        f"{confidence}%"

    )




st.divider()



# ==================================================
# Historical Chart
# ==================================================

st.subheader(

    "📉 Historical Sentiment Pattern"

)



history_chart = pd.DataFrame(

{

"Analysis":

df["index"],


"Sentiment Score":

df["score"]

}

)



st.line_chart(

    history_chart.set_index("Analysis")

)




# ==================================================
# Future Prediction Chart
# ==================================================

st.subheader(

    "🔮 7-Day AI Forecast"

)



forecast_chart = pd.DataFrame(

{

"Day":

[

f"Day {i+1}"

for i in range(future_days)

],


"Predicted Sentiment":

prediction

}

)



st.line_chart(

    forecast_chart.set_index("Day")

)




# ==================================================
# AI Recommendation
# ==================================================

st.divider()



st.subheader(

    "🤖 AI Business Recommendation"

)



st.info(

    recommendation

)



# ==================================================
# Forecast Table
# ==================================================

st.subheader(

    "📅 Forecast Details"

)



st.dataframe(

forecast_chart,

use_container_width=True

)



st.success(

"AI trend prediction completed successfully."

)