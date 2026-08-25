import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from pytrends.request import TrendReq
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

import plotly.graph_objects as go


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Trend Prediction (Google Trends)",
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
# FULL HD UI THEME
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(circle at top right,
                rgba(75, 74, 255, 0.12),
                transparent 30%
            ),
            #050816;
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1750px;
    }

    h1, h2, h3 {
        color: #f9fafb;
    }

    .kpi-card {
        background: linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.98),
            rgba(8, 18, 34, 0.98)
        );
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 16px;
        padding: 18px 20px;
        min-height: 140px;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.55);
    }

    .kpi-label {
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 6px;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #f9fafb;
        line-height: 1.2;
    }

    .kpi-sub {
        margin-top: 8px;
        color: #6b7280;
        font-size: 13px;
    }

    .positive { color: #22c55e; }
    .negative { color: #ef4444; }
    .neutral  { color: #facc15; }
    .blue     { color: #60a5fa; }
    .purple   { color: #a855f7; }

    .panel-title {
        font-size: 18px;
        font-weight: 700;
        color: #f9fafb;
        margin-bottom: 10px;
    }

    .forecast-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(148, 163, 184, 0.25);
        padding: 8px 2px;
        font-size: 13px;
    }

    .mode-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.45);
        padding: 12px 16px;
        border-radius: 12px;
        font-size: 13px;
        color: #e5e7eb;
    }

    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns([5, 2])

with header_left:
    st.title("📈 AI Trend Prediction (Google Trends)")
    st.caption("Real-time Google Trends analysis with 7-day AI forecast.")

with header_right:
    st.write(f"Logged in as **{user['name']}**")
    st.caption("Smart Social Analytics • Trend Engine")

st.divider()


# =========================================================
# KEYWORD INPUT
# =========================================================

st.subheader("🔍 Choose Keyword for Trend Analysis")

col_kw1, col_kw2 = st.columns([2, 1])

with col_kw1:
    keyword = st.text_input(
        "Search keyword (e.g. 'instagram', 'ai', 'bitcoin')",
        value="social media"
    )

with col_kw2:
    timeframe = st.selectbox(
        "Historical period",
        ["today 3-m", "today 12-m", "today 5-y"],
        index=1
    )

region = st.selectbox(
    "Region",
    ["", "AU", "US", "GB", "IN"],
    index=0
)

st.divider()


# =========================================================
# LOAD GOOGLE TRENDS DATA (SAFE)
# =========================================================

if not keyword.strip():
    st.warning("Please enter a keyword.")
    st.stop()

with st.spinner("Fetching Google Trends data..."):
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload([keyword], timeframe=timeframe, geo=region)

        iot = pytrends.interest_over_time()

        if iot.empty:
            st.info("No Google Trends data returned.")
            st.stop()

        # Remove partial rows safely
        if "isPartial" in iot.columns:
            iot = iot[iot["isPartial"] == False]

        trends_df = iot.reset_index()[["date", keyword]]
        trends_df.rename(columns={keyword: "interest"}, inplace=True)

    except Exception as e:
        st.error("Unable to connect to Google Trends.")
        st.exception(e)
        st.stop()


# =========================================================
# PREPARE DATA
# =========================================================

trends_df["date"] = pd.to_datetime(trends_df["date"])
trends_df = trends_df.sort_values("date").reset_index(drop=True)

trends_df["time_index"] = np.arange(len(trends_df))

X = trends_df[["time_index"]]
y = trends_df["interest"].astype(float)

model = LinearRegression()
model.fit(X, y)

historical_fit = model.predict(X)
mae = mean_absolute_error(y, historical_fit)


# =========================================================
# FUTURE FORECAST (7 DAYS)
# =========================================================

future_days = 7
future_indexes = np.arange(len(trends_df), len(trends_df) + future_days).reshape(-1, 1)
raw_prediction = model.predict(future_indexes)

recent_avg = float(trends_df["interest"].tail(min(7, len(trends_df))).mean())
stabilised_prediction = raw_prediction * 0.6 + recent_avg * 0.4
future_prediction = np.clip(stabilised_prediction, 0, 100)

last_real_date = trends_df["date"].max().normalize()
future_dates = [last_real_date + timedelta(days=i) for i in range(1, future_days + 1)]

forecast_df = pd.DataFrame({
    "date": future_dates,
    "interest": future_prediction
})


# =========================================================
# KPI METRICS
# =========================================================

current_interest = float(trends_df["interest"].iloc[-1])
avg_interest = float(trends_df["interest"].mean())
peak_interest = float(trends_df["interest"].max())
forecast_avg = float(forecast_df["interest"].mean())

change = future_prediction[-1] - current_interest

if change > 5:
    direction = "Increasing"
    direction_icon = "↗"
    direction_class = "positive"
elif change < -5:
    direction = "Decreasing"
    direction_icon = "↘"
    direction_class = "negative"
else:
    direction = "Stable"
    direction_icon = "→"
    direction_class = "neutral"

forecast_reliability = round(
    max(0, min((1 - mae / 100) * 100, 95)),
    1
)


st.markdown(
    f'<div class="mode-card">'
    f'<b>Data Source:</b> Google Trends<br>'
    f'Keyword: <b>{keyword}</b> • Timeframe: <b>{timeframe}</b> • Region: <b>{region or "Worldwide"}</b>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# KPI CARDS
# =========================================================

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Current Interest</div>'
        f'<div class="kpi-value">{current_interest:.1f}</div>'
        f'<div class="kpi-sub blue">Scale 0–100</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Average Interest</div>'
        f'<div class="kpi-value">{avg_interest:.1f}</div>'
        f'<div class="kpi-sub">Across timeframe</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Peak Interest</div>'
        f'<div class="kpi-value">{peak_interest:.1f}</div>'
        f'<div class="kpi-sub purple">Highest recorded</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Forecast (Next 7 Days)</div>'
        f'<div class="kpi-value">{direction}</div>'
        f'<div class="kpi-sub {direction_class}">{direction_icon} Reliability: {forecast_reliability:.1f}%</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with k5:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">Avg Forecast Interest</div>'
        f'<div class="kpi-value">{forecast_avg:.1f}</div>'
        f'<div class="kpi-sub">Modelled from history</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# MAIN CHART
# =========================================================

chart_col, forecast_col = st.columns([2.3, 1])

with chart_col:
    st.markdown(
        '<div class="panel-title">📊 Historical Interest + 7-Day Forecast</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=trends_df["date"],
            y=trends_df["interest"],
            mode="lines+markers",
            name="Historical",
            line=dict(width=3, color="#22c55e"),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.12)"
        )
    )

    forecast_x = [trends_df["date"].iloc[-1]] + list(forecast_df["date"])
    forecast_y = [current_interest] + list(forecast_df["interest"])

    fig.add_trace(
        go.Scatter(
            x=forecast_x,
            y=forecast_y,
            mode="lines+markers",
            name="Forecast",
            line=dict(width=3, dash="dash", color="#60a5fa"),
            marker=dict(size=6)
        )
    )

    fig.add_vline(
        x=trends_df["date"].iloc[-1],
        line_dash="dash",
        line_color="rgba(148,163,184,0.7)"
    )

    fig.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#020617",
        font=dict(color="#e5e7eb"),
        legend=dict(orientation="h", y=1.08, x=0.35),
        xaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.15)"),
        yaxis=dict(
            title="Google Trends Interest (0–100)",
            range=[0, 105],
            showgrid=True,
            gridcolor="rgba(148,163,184,0.15)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


with forecast_col:
    st.markdown(
        '<div class="panel-title">🔮 7-Day Interest Forecast</div>',
        unsafe_allow_html=True
    )

    for _, row in forecast_df.iterrows():
        day = row["date"].strftime("%d %b")
        val = float(row["interest"])

        if val >= current_interest + 5:
            icon = "🟢"
            css = "positive"
            label = "Higher"
        elif val <= current_interest - 5:
            icon = "🔴"
            css = "negative"
            label = "Lower"
        else:
            icon = "🟡"
            css = "neutral"
            label = "Similar"

        st.markdown(
            f'<div class="forecast-row">'
            f'<div>{day}</div>'
            f'<div class="{css}">{icon} {label}</div>'
            f'<div>{val:.1f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if direction_class == "positive":
        st.success("📈 Overall Outlook: Interest is likely to increase.")
    elif direction_class == "negative":
        st.error("📉 Overall Outlook: Interest may decline.")
    else:
        st.info("➡️ Overall Outlook: Interest is relatively stable.")


# =========================================================
# RAW DATA
# =========================================================

st.divider()
st.subheader("📋 Raw Google Trends Data")
st.dataframe(trends_df.tail(30), use_container_width=True)
