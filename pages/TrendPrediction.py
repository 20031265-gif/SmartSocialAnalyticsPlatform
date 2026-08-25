import streamlit as st
from firebase_config import db

import pandas as pd
import numpy as np
import re

from collections import Counter
from datetime import datetime, timedelta

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

import plotly.graph_objects as go


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Trend Prediction",
    page_icon="📈",
    layout="wide"
)


# =========================================================
# LOGIN CHECK
# =========================================================

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Please login first.")
    st.stop()

user = st.session_state["user"]


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(75, 74, 255, 0.08),
                transparent 30%
            ),
            #07101f;
        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1750px;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    .kpi-card {
        background: linear-gradient(
            145deg,
            rgba(15, 28, 49, 0.98),
            rgba(8, 18, 34, 0.98)
        );

        border:
            1px solid rgba(125, 145, 180, 0.18);

        border-radius: 15px;

        padding: 20px;

        min-height: 145px;

        box-shadow:
            0 10px 30px rgba(0,0,0,0.25);
    }

    .kpi-label {
        color: #aebbd1;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 27px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }

    .kpi-sub {
        margin-top: 10px;
        color: #7f8ea6;
        font-size: 13px;
    }

    .positive {
        color: #35d07f;
    }

    .negative {
        color: #ff5d64;
    }

    .neutral {
        color: #ffbd38;
    }

    .blue {
        color: #4c86ff;
    }

    .purple {
        color: #9a61ff;
    }

    .panel-title {
        font-size: 19px;
        font-weight: 700;
        color: white;
        margin-bottom: 12px;
    }

    .forecast-row {
        display: flex;
        justify-content: space-between;
        align-items: center;

        border-bottom:
            1px solid rgba(255,255,255,0.07);

        padding: 10px 2px;

        font-size: 14px;
    }

    .topic-row {
        display: grid;

        grid-template-columns:
            35px 1fr 90px 70px;

        align-items: center;

        border-bottom:
            1px solid rgba(255,255,255,0.06);

        padding: 10px 0;

        gap: 8px;
    }

    .topic-rank {
        width: 26px;
        height: 26px;

        border-radius: 8px;

        background: #14243d;

        display: flex;

        align-items: center;

        justify-content: center;

        color: #c7d2e5;

        font-size: 12px;
    }

    .insight-card {
        background:
            rgba(13, 27, 48, 0.85);

        border:
            1px solid rgba(255,255,255,0.08);

        border-radius: 12px;

        padding: 15px;

        min-height: 165px;
    }

    .insight-text {
        font-size: 14px;
        color: #e8eef9;
        margin-bottom: 10px;
    }

    .insight-meta {
        color: #7f8da5;
        font-size: 12px;
        margin-top: 8px;
    }

    .mode-card {
        background:
            rgba(14, 27, 48, 0.8);

        border:
            1px solid rgba(87, 110, 150, 0.18);

        padding: 12px 16px;

        border-radius: 10px;

        font-size: 13px;

        color: #aebbd1;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns(
    [5, 2]
)


with header_left:

    st.title(
        "📈 AI Trend Prediction Dashboard"
    )

    st.caption(
        "Predict future social media sentiment behaviour "
        "using Artificial Intelligence"
    )


with header_right:

    if st.button(
        "✨ Generate New Forecast",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()


# =========================================================
# LOAD FIRESTORE DATA
# =========================================================

@st.cache_data(
    ttl=30,
    show_spinner=False
)
def load_sentiment_history(uid):

    records = db.collection(
        "history"
    ).stream()

    result = []

    for record in records:

        item = record.to_dict()

        if item.get(
            "user_id"
        ) == uid:

            result.append(
                item
            )

    return result


with st.spinner(
    "Loading sentiment intelligence..."
):

    data = load_sentiment_history(
        user["uid"]
    )


df = pd.DataFrame(
    data
)


if df.empty:

    st.info(
        "No sentiment data is available yet. "
        "Go to Sentiment and analyse some posts first."
    )

    st.stop()


# =========================================================
# VALIDATION
# =========================================================

if "sentiment" not in df.columns:

    st.error(
        "The history collection does not contain sentiment data."
    )

    st.stop()


if "created_at" not in df.columns:

    st.error(
        "Historical records do not contain created_at timestamps."
    )

    st.stop()


# =========================================================
# CLEAN DATA
# =========================================================

sentiment_map = {
    "POSITIVE": 1,
    "NEUTRAL": 0,
    "NEGATIVE": -1
}


df["sentiment"] = (
    df["sentiment"]
    .astype(str)
    .str.upper()
)


df["score"] = df[
    "sentiment"
].map(
    sentiment_map
)


df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce"
)


df = df.dropna(
    subset=[
        "created_at",
        "score"
    ]
)


df = df.sort_values(
    "created_at"
).reset_index(
    drop=True
)


if df.empty:

    st.warning(
        "No valid sentiment records are available."
    )

    st.stop()


# =========================================================
# PERIOD FILTER
# =========================================================

maximum_date = df[
    "created_at"
].max().date()


filter_col1, filter_col2 = st.columns(
    [4, 1]
)


with filter_col1:

    selected_range = st.radio(
        "Historical period",
        [
            "7D",
            "30D",
            "90D",
            "All"
        ],
        horizontal=True,
        index=1
    )


with filter_col2:

    st.caption(
        "Latest record"
    )

    st.write(
        maximum_date.strftime(
            "%d %b %Y"
        )
    )


if selected_range == "7D":

    cutoff = maximum_date - timedelta(
        days=7
    )

    filtered_df = df[
        df[
            "created_at"
        ].dt.date >= cutoff
    ].copy()


elif selected_range == "30D":

    cutoff = maximum_date - timedelta(
        days=30
    )

    filtered_df = df[
        df[
            "created_at"
        ].dt.date >= cutoff
    ].copy()


elif selected_range == "90D":

    cutoff = maximum_date - timedelta(
        days=90
    )

    filtered_df = df[
        df[
            "created_at"
        ].dt.date >= cutoff
    ].copy()


else:

    filtered_df = df.copy()


if filtered_df.empty:

    filtered_df = df.copy()


# =========================================================
# DAILY DATA
# =========================================================

filtered_df[
    "date"
] = filtered_df[
    "created_at"
].dt.date


daily_real = (
    filtered_df
    .groupby(
        "date"
    )
    .agg(

        sentiment_score=(
            "score",
            "mean"
        ),

        mentions=(
            "score",
            "count"
        )

    )
    .reset_index()
)


daily_real[
    "date"
] = pd.to_datetime(
    daily_real[
        "date"
    ]
)


daily_real = daily_real.sort_values(
    "date"
)


# =========================================================
# FORECASTING MODE
# =========================================================

# If there are at least 3 genuinely different dates,
# use real date-based forecasting.
#
# Otherwise, use sequential windows of posts.
#
# This avoids inventing fake historical dates.


if len(daily_real) >= 3:

    forecasting_mode = (
        "Real Date-Based Forecast"
    )

    model_df = daily_real.copy()

    model_df[
        "time_index"
    ] = np.arange(
        len(model_df)
    )

    chart_labels = model_df[
        "date"
    ]

    model_description = (
        "Forecast generated from genuine daily "
        "historical sentiment records."
    )


else:

    forecasting_mode = (
        "Sequential Sentiment Window Forecast"
    )

    # ---------------------------------------------
    # Determine window size
    # ---------------------------------------------

    total_records = len(
        filtered_df
    )


    if total_records >= 100:

        window_size = 10

    elif total_records >= 50:

        window_size = 8

    elif total_records >= 25:

        window_size = 5

    else:

        window_size = 3


    sequential = filtered_df.copy()

    sequential[
        "window"
    ] = (
        np.arange(
            len(sequential)
        )
        //
        window_size
    )


    model_df = (
        sequential
        .groupby(
            "window"
        )
        .agg(

            sentiment_score=(
                "score",
                "mean"
            ),

            mentions=(
                "score",
                "count"
            )

        )
        .reset_index()
    )


    if len(model_df) < 3:

        st.warning(
            """
            There is not enough historical information
            to produce a reliable trend forecast yet.
            """
        )

        st.info(
            "Analyse more social media posts and try again."
        )

        st.stop()


    model_df[
        "time_index"
    ] = np.arange(
        len(model_df)
    )


    model_df[
        "date"
    ] = pd.date_range(
        end=maximum_date,
        periods=len(
            model_df
        ),
        freq="D"
    )


    chart_labels = model_df[
        "date"
    ]


    model_description = (
        "Insufficient multi-day history was available, "
        "so the prototype is using sequential groups "
        "of analysed posts to estimate short-term "
        "sentiment direction."
    )


# =========================================================
# MODEL TRAINING
# =========================================================

X = model_df[
    [
        "time_index"
    ]
]


y = model_df[
    "sentiment_score"
]


model = LinearRegression()


model.fit(
    X,
    y
)


historical_fit = model.predict(
    X
)


mae = mean_absolute_error(
    y,
    historical_fit
)


if len(
    model_df
) > 2:

    r2 = r2_score(
        y,
        historical_fit
    )

else:

    r2 = 0.0


# =========================================================
# FUTURE FORECAST
# =========================================================

future_days = 7


future_indexes = np.arange(
    len(model_df),
    len(model_df) + future_days
).reshape(
    -1,
    1
)


raw_prediction = model.predict(
    future_indexes
)


# =========================================================
# PREVENT EXTREME UNREALISTIC EXTRAPOLATION
# =========================================================

# Linear regression can shoot straight to +1 or -1
# when history is limited.
#
# Blend the regression forecast slightly toward
# the recent historical sentiment average.


recent_average = float(
    model_df[
        "sentiment_score"
    ].tail(
        min(
            3,
            len(model_df)
        )
    ).mean()
)


stabilised_prediction = (
    raw_prediction * 0.55
    +
    recent_average * 0.45
)


future_prediction = np.clip(
    stabilised_prediction,
    -1,
    1
)


# =========================================================
# FUTURE DATES
# =========================================================

last_real_date = df[
    "created_at"
].max().normalize()


future_dates = [

    last_real_date
    +
    timedelta(
        days=i
    )

    for i in range(
        1,
        future_days + 1
    )

]


forecast_df = pd.DataFrame(
    {
        "date":
            future_dates,

        "score":
            future_prediction
    }
)


# =========================================================
# SENTIMENT LABEL
# =========================================================

def sentiment_label(
    score
):

    if score > 0.25:

        return "POSITIVE"

    elif score < -0.25:

        return "NEGATIVE"

    else:

        return "NEUTRAL"


forecast_df[
    "sentiment"
] = forecast_df[
    "score"
].apply(
    sentiment_label
)


# =========================================================
# CURRENT METRICS
# =========================================================

current_score = float(
    filtered_df[
        "score"
    ].tail(
        min(
            10,
            len(filtered_df)
        )
    ).mean()
)


current_sentiment = sentiment_label(
    current_score
)


average_forecast = float(
    np.mean(
        future_prediction
    )
)


predicted_sentiment = sentiment_label(
    average_forecast
)


# =========================================================
# DIRECTION
# =========================================================

forecast_change = float(
    future_prediction[-1]
    -
    future_prediction[0]
)


if forecast_change > 0.05:

    direction = "Increasing"
    direction_icon = "↗"
    direction_class = "positive"


elif forecast_change < -0.05:

    direction = "Decreasing"
    direction_icon = "↘"
    direction_class = "negative"


else:

    direction = "Stable"
    direction_icon = "→"
    direction_class = "neutral"


# =========================================================
# FORECAST RELIABILITY
# =========================================================

data_quality = min(
    len(
        filtered_df
    ) / 100,
    1
)


history_quality = min(
    len(
        model_df
    ) / 10,
    1
)


error_quality = max(
    0,
    1 - mae
)


forecast_reliability = (
    data_quality * 0.30
    +
    history_quality * 0.25
    +
    error_quality * 0.45
) * 100


# Reduce reliability for fallback mode

if forecasting_mode == (
    "Sequential Sentiment Window Forecast"
):

    forecast_reliability *= 0.85


forecast_reliability = round(
    max(
        0,
        min(
            forecast_reliability,
            95
        )
    ),
    1
)


# =========================================================
# DISTRIBUTION
# =========================================================

total_mentions = len(
    filtered_df
)


positive_count = int(
    (
        filtered_df[
            "sentiment"
        ]
        ==
        "POSITIVE"
    ).sum()
)


neutral_count = int(
    (
        filtered_df[
            "sentiment"
        ]
        ==
        "NEUTRAL"
    ).sum()
)


negative_count = int(
    (
        filtered_df[
            "sentiment"
        ]
        ==
        "NEGATIVE"
    ).sum()
)


positive_percent = (
    positive_count
    /
    max(
        total_mentions,
        1
    )
    *
    100
)


neutral_percent = (
    neutral_count
    /
    max(
        total_mentions,
        1
    )
    *
    100
)


negative_percent = (
    negative_count
    /
    max(
        total_mentions,
        1
    )
    *
    100
)


# =========================================================
# FORECAST MODE INFORMATION
# =========================================================

st.markdown(
    f'<div class="mode-card">'
    f'<b>Forecast Mode:</b> {forecasting_mode}'
    f'<br>'
    f'{model_description}'
    f'</div>',
    unsafe_allow_html=True
)


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# =========================================================
# KPI HELPERS
# =========================================================

sentiment_emoji = {
    "POSITIVE": "😊",
    "NEUTRAL": "😐",
    "NEGATIVE": "😡"
}


sentiment_css = {
    "POSITIVE": "positive",
    "NEUTRAL": "neutral",
    "NEGATIVE": "negative"
}


# =========================================================
# KPI CARDS
# =========================================================

k1, k2, k3, k4, k5 = st.columns(
    5
)


with k1:

    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">'
        f'Current Trend'
        f'</div>'
        f'<div class="kpi-value">'
        f'{current_sentiment.title()} '
        f'{sentiment_emoji[current_sentiment]}'
        f'</div>'
        f'<div class="kpi-sub '
        f'{sentiment_css[current_sentiment]}">'
        f'Current sentiment score: '
        f'{current_score:.2f}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with k2:

    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">'
        f'Prediction (Next 7 Days)'
        f'</div>'
        f'<div class="kpi-value">'
        f'{direction}'
        f'</div>'
        f'<div class="kpi-sub '
        f'{direction_class}">'
        f'{direction_icon} '
        f'Forecast reliability: '
        f'{forecast_reliability:.1f}%'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with k3:

    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">'
        f'Predicted Sentiment Score'
        f'</div>'
        f'<div class="kpi-value">'
        f'{average_forecast:.2f} '
        f'<span '
        f'style="font-size:14px;'
        f'color:#73829a;">'
        f'/ 1.00'
        f'</span>'
        f'</div>'
        f'<div class="kpi-sub">'
        f'Range: -1 Negative to +1 Positive'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with k4:

    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">'
        f'Total Posts Analysed'
        f'</div>'
        f'<div class="kpi-value">'
        f'{total_mentions:,}'
        f'</div>'
        f'<div class="kpi-sub purple">'
        f'Firebase sentiment history'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with k5:

    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">'
        f'Forecast Reliability'
        f'</div>'
        f'<div class="kpi-value neutral">'
        f'{forecast_reliability:.1f}%'
        f'</div>'
        f'<div class="kpi-sub">'
        f'Based on available historical data'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# =========================================================
# MAIN CHART + FORECAST
# =========================================================

chart_column, forecast_column = st.columns(
    [
        2.3,
        1
    ]
)


# =========================================================
# CHART
# =========================================================

with chart_column:

    st.markdown(
        '<div class="panel-title">'
        '📊 Historical Sentiment Trend'
        '</div>',
        unsafe_allow_html=True
    )


    figure = go.Figure()


    figure.add_trace(
        go.Scatter(

            x=model_df[
                "date"
            ],

            y=model_df[
                "sentiment_score"
            ],

            mode="lines+markers",

            name="Historical",

            line=dict(
                width=3,
                color="#35d07f"
            ),

            marker=dict(
                size=7
            ),

            fill="tozeroy",

            fillcolor=(
                "rgba(53,208,127,0.08)"
            )
        )
    )


    forecast_x = (
        [
            model_df[
                "date"
            ].iloc[-1]
        ]
        +
        list(
            forecast_df[
                "date"
            ]
        )
    )


    forecast_y = (
        [
            model_df[
                "sentiment_score"
            ].iloc[-1]
        ]
        +
        list(
            forecast_df[
                "score"
            ]
        )
    )


    figure.add_trace(
        go.Scatter(

            x=forecast_x,

            y=forecast_y,

            mode="lines+markers",

            name="Forecast",

            line=dict(
                width=3,
                dash="dash",
                color="#4c86ff"
            ),

            marker=dict(
                size=7
            )
        )
    )


    figure.add_hline(
        y=0,
        line_dash="dot",
        line_color=(
            "rgba(255,255,255,0.18)"
        )
    )


    figure.add_vline(
        x=model_df[
            "date"
        ].iloc[-1],

        line_dash="dash",

        line_color=(
            "rgba(255,255,255,0.45)"
        )
    )


    figure.update_layout(

        height=430,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        plot_bgcolor="#081426",

        font=dict(
            color="#cbd5e1"
        ),

        legend=dict(
            orientation="h",
            y=1.08,
            x=0.35
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor=(
                "rgba(255,255,255,0.04)"
            )
        ),

        yaxis=dict(
            range=[
                -1.05,
                1.05
            ],

            title="Sentiment Score",

            showgrid=True,

            gridcolor=(
                "rgba(255,255,255,0.05)"
            )
        )
    )


    st.plotly_chart(
        figure,
        use_container_width=True
    )


# =========================================================
# 7 DAY FORECAST
# =========================================================

with forecast_column:

    st.markdown(
        '<div class="panel-title">'
        '🔮 7-Day Trend Forecast'
        '</div>',
        unsafe_allow_html=True
    )


    for _, row in forecast_df.iterrows():

        predicted = row[
            "sentiment"
        ]

        score = float(
            row[
                "score"
            ]
        )


        if predicted == "POSITIVE":

            icon = "🟢"
            css = "positive"


        elif predicted == "NEGATIVE":

            icon = "🔴"
            css = "negative"


        else:

            icon = "🟡"
            css = "neutral"


        st.markdown(
            f'<div class="forecast-row">'
            f'<div>'
            f'{row["date"].strftime("%d %b")}'
            f'</div>'
            f'<div class="{css}">'
            f'{icon} '
            f'{predicted.title()}'
            f'</div>'
            f'<div>'
            f'{score:+.2f}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    if predicted_sentiment == "POSITIVE":

        st.success(
            "📈 Overall Outlook: Positive"
        )


    elif predicted_sentiment == "NEGATIVE":

        st.error(
            "📉 Overall Outlook: Negative"
        )


    else:

        st.info(
            "➡️ Overall Outlook: Stable"
        )


# =========================================================
# SECOND ROW
# =========================================================

distribution_column, topics_column, factors_column = (
    st.columns(
        [
            1,
            1.65,
            1.25
        ]
    )
)


# =========================================================
# SENTIMENT DISTRIBUTION
# =========================================================

with distribution_column:

    st.markdown(
        '<div class="panel-title">'
        '😊 Sentiment Distribution'
        '</div>',
        unsafe_allow_html=True
    )


    donut = go.Figure(
        data=[
            go.Pie(

                labels=[
                    "Positive",
                    "Neutral",
                    "Negative"
                ],

                values=[
                    positive_count,
                    neutral_count,
                    negative_count
                ],

                hole=0.65,

                marker=dict(
                    colors=[
                        "#32d27c",
                        "#ffbd36",
                        "#ff525d"
                    ]
                ),

                textinfo="none"
            )
        ]
    )


    donut.update_layout(

        height=320,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),

        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),

        font=dict(
            color="white"
        ),

        annotations=[
            dict(

                text=(
                    f"<b>{total_mentions:,}</b>"
                    "<br>Total"
                ),

                x=0.5,
                y=0.5,

                showarrow=False,

                font=dict(
                    size=18
                )
            )
        ],

        legend=dict(
            orientation="h",
            y=-0.05
        )
    )


    st.plotly_chart(
        donut,
        use_container_width=True
    )


    st.caption(
        f"""
        🟢 Positive: {positive_count:,} ({positive_percent:.1f}%)

        🟡 Neutral: {neutral_count:,} ({neutral_percent:.1f}%)

        🔴 Negative: {negative_count:,} ({negative_percent:.1f}%)
        """
    )


# =========================================================
# TOPIC EXTRACTION
# =========================================================

def extract_topics(
    dataframe
):

    if "text" not in dataframe.columns:

        return []


    stop_words = {

        "the",
        "and",
        "this",
        "that",
        "with",
        "for",
        "from",
        "your",
        "you",
        "are",
        "was",
        "were",
        "have",
        "has",
        "had",
        "but",
        "not",
        "very",
        "today",
        "tomorrow",
        "just",
        "really",
        "about",
        "into",
        "our",
        "their",
        "they",
        "will",
        "would",
        "could",
        "new",
        "there",
        "when",
        "what",
        "which",
        "been",
        "being",

        "love",
        "amazing",
        "great",
        "good",
        "bad",
        "terrible",
        "wonderful",
        "slow",
        "happy",
        "excellent",
        "disappointed",
        "fantastic",
        "frustrating",
        "pleased",

        "amir"
    }


    words = []


    for text in dataframe[
        "text"
    ].dropna():

        text = str(
            text
        ).lower()


        hashtags = re.findall(
            r"#\w+",
            text
        )


        normal_words = re.findall(
            r"\b[a-zA-Z]{4,}\b",
            text
        )


        for word in (
            hashtags
            +
            normal_words
        ):

            cleaned = word.lower()

            if cleaned not in stop_words:

                words.append(
                    cleaned
                )


    return Counter(
        words
    ).most_common(
        5
    )


top_topics = extract_topics(
    filtered_df
)


# =========================================================
# TOPICS
# =========================================================

with topics_column:

    st.markdown(
        '<div class="panel-title">'
        '🔥 Top Topics Driving Trends'
        '</div>',
        unsafe_allow_html=True
    )


    if not top_topics:

        st.info(
            "Not enough text data to identify topics."
        )


    else:

        for rank, (
            topic,
            count
        ) in enumerate(
            top_topics,
            start=1
        ):

            percentage = (
                count
                /
                max(
                    total_mentions,
                    1
                )
                *
                100
            )


            if topic.startswith(
                "#"
            ):

                display_topic = topic

            else:

                display_topic = (
                    "#"
                    +
                    topic.title()
                )


            st.markdown(
                f'<div class="topic-row">'
                f'<div class="topic-rank">'
                f'{rank}'
                f'</div>'
                f'<div>'
                f'<b>{display_topic}</b>'
                f'</div>'
                f'<div>'
                f'{count} mentions'
                f'</div>'
                f'<div class="positive">'
                f'{percentage:.1f}%'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )


# =========================================================
# KEY FACTORS
# =========================================================

with factors_column:

    st.markdown(
        '<div class="panel-title">'
        '⚡ Key Factors Influencing Trend'
        '</div>',
        unsafe_allow_html=True
    )


    factors = []


    if positive_percent >= 45:

        factors.append(
            (
                "😊 Positive User Feedback",
                "High Impact",
                "positive"
            )
        )


    if negative_percent >= 30:

        factors.append(
            (
                "⚠️ Negative Feedback",
                "High Impact",
                "negative"
            )
        )


    if neutral_percent >= 30:

        factors.append(
            (
                "📰 Informational Discussion",
                "Medium Impact",
                "neutral"
            )
        )


    if top_topics:

        main_topic = (
            top_topics[
                0
            ][
                0
            ]
            .replace(
                "#",
                ""
            )
            .title()
        )

        factors.append(
            (
                f"🔥 {main_topic} Discussion",
                "High Impact",
                "positive"
            )
        )


    if forecasting_mode == (
        "Sequential Sentiment Window Forecast"
    ):

        factors.append(
            (
                "🕒 Limited Multi-Day History",
                "Medium Impact",
                "neutral"
            )
        )


    if len(
        factors
    ) == 0:

        factors.append(
            (
                "📊 Stable Audience Activity",
                "Low Impact",
                "blue"
            )
        )


    for (
        title,
        impact,
        css
    ) in factors[:5]:

        st.markdown(
            f'<div class="forecast-row">'
            f'<div>{title}</div>'
            f'<div class="{css}">'
            f'{impact}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# =========================================================
# THIRD ROW
# =========================================================

recent_column, opportunity_column = st.columns(
    [
        2.3,
        1
    ]
)


# =========================================================
# RECENT SENTIMENT INSIGHTS
# =========================================================

with recent_column:

    st.markdown(
        '<div class="panel-title">'
        '💬 Recent Sentiment Insights'
        '</div>',
        unsafe_allow_html=True
    )


    recent = (
        filtered_df
        .sort_values(
            "created_at",
            ascending=False
        )
        .head(
            3
        )
    )


    insight_columns = st.columns(
        3
    )


    for column, (
        _,
        item
    ) in zip(
        insight_columns,
        recent.iterrows()
    ):

        sentiment = item[
            "sentiment"
        ]


        if sentiment == "POSITIVE":

            icon = "😊"
            css = "positive"


        elif sentiment == "NEGATIVE":

            icon = "😡"
            css = "negative"


        else:

            icon = "😐"
            css = "neutral"


        text = str(
            item.get(
                "text",
                "No text available"
            )
        )


        if len(
            text
        ) > 110:

            text = (
                text[
                    :107
                ]
                +
                "..."
            )


        confidence = item.get(
            "confidence",
            0
        )


        source = item.get(
            "source",
            "Sentiment"
        )


        with column:

            st.markdown(
                f'<div class="insight-card">'
                f'<div class="insight-text">'
                f'"{text}"'
                f'</div>'
                f'<div class="{css}">'
                f'{icon} '
                f'{sentiment.title()}'
                f'</div>'
                f'<div class="insight-meta">'
                f'Confidence: '
                f'{confidence}%'
                f'<br>'
                f'Source: '
                f'{source}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )


# =========================================================
# TREND OPPORTUNITIES
# =========================================================

with opportunity_column:

    st.markdown(
        '<div class="panel-title">'
        '🚀 Trend Opportunities'
        '</div>',
        unsafe_allow_html=True
    )


    if predicted_sentiment == "POSITIVE":

        opportunities = [
            (
                "Increase Engagement",
                forecast_reliability
            ),

            (
                "Promote Positive Content",
                max(
                    forecast_reliability - 5,
                    0
                )
            ),

            (
                "Expand Campaign Reach",
                max(
                    forecast_reliability - 10,
                    0
                )
            )
        ]


    elif predicted_sentiment == "NEGATIVE":

        opportunities = [
            (
                "Review Complaints",
                forecast_reliability
            ),

            (
                "Customer Recovery",
                max(
                    forecast_reliability - 5,
                    0
                )
            ),

            (
                "Reputation Monitoring",
                max(
                    forecast_reliability - 10,
                    0
                )
            )
        ]


    else:

        opportunities = [
            (
                "Increase Engagement",
                forecast_reliability
            ),

            (
                "Content Testing",
                max(
                    forecast_reliability - 5,
                    0
                )
            ),

            (
                "Audience Monitoring",
                max(
                    forecast_reliability - 10,
                    0
                )
            )
        ]


    opportunity_df = pd.DataFrame(
        {
            "Opportunity": [
                item[
                    0
                ]
                for item in opportunities
            ],

            "Confidence": [
                f"{item[1]:.1f}%"
                for item in opportunities
            ]
        }
    )


    st.dataframe(
        opportunity_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# MODEL DETAILS
# =========================================================

with st.expander(
    "🧠 AI Forecast Model Details"
):

    c1, c2, c3, c4 = st.columns(
        4
    )


    c1.metric(
        "Posts Used",
        len(
            filtered_df
        )
    )


    c2.metric(
        "Trend Periods",
        len(
            model_df
        )
    )


    c3.metric(
        "Mean Absolute Error",
        f"{mae:.3f}"
    )


    c4.metric(
        "R² Score",
        f"{r2:.3f}"
    )


    st.write(
        f"**Forecast mode:** "
        f"{forecasting_mode}"
    )


    st.info(
        """
        **Forecasting method: Linear Regression**

        Sentiment values are converted into numerical scores:

        - Positive = +1
        - Neutral = 0
        - Negative = -1

        When enough genuine historical dates are available,
        the model forecasts using daily sentiment averages.

        When there are not enough different dates, the prototype
        uses sequential groups of analysed posts to estimate the
        short-term sentiment direction.

        The future regression result is also stabilised using the
        recent historical average to reduce unrealistic extreme
        predictions from limited data.

        Forecast Reliability is an internal prototype indicator.
        It is not formal model accuracy.
        """
    )


# =========================================================
# BUSINESS RECOMMENDATION
# =========================================================

st.markdown(
    "<br>",
    unsafe_allow_html=True
)


st.subheader(
    "🤖 AI Business Recommendation"
)


if (
    predicted_sentiment
    ==
    "POSITIVE"
):

    st.success(
        """
        **Positive sentiment is expected over the forecast period.**

        Continue engaging with successful content, identify
        topics producing favourable reactions and maintain
        active interaction with users.
        """
    )


elif (
    predicted_sentiment
    ==
    "NEGATIVE"
):

    st.error(
        """
        **Negative sentiment is expected over the forecast period.**

        Review recent complaints, identify repeated concerns
        and respond quickly to emerging issues. Increased
        monitoring is recommended.
        """
    )


else:

    st.info(
        """
        **Sentiment is expected to remain relatively stable.**

        Continue monitoring audience reactions and test
        different content strategies to identify opportunities
        for stronger positive engagement.
        """
    )


# =========================================================
# LAST UPDATED
# =========================================================

st.caption(
    "Last updated: "
    +
    datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )
)