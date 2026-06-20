import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="City Smart Pulse — Roorkee",
    page_icon="🏙️",
    layout="wide"
)

# ─── CUSTOM CSS (makes it look premium) ──────────────────
st.markdown("""
    <style>
    /* Background */
    .stApp { background-color: #0f1117; }

    /* Title */
    h1 { color: #00d4ff !important; text-align: center; }
    h2, h3 { color: #ffffff !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #00d4ff;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        color: #aaaaaa;
        font-size: 16px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #00d4ff !important;
        border-bottom: 3px solid #00d4ff;
    }

    /* Sidebar */
    .css-1d391kg { background-color: #1e2130; }
    </style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────
st.markdown("<h1>🏙️ City Smart Pulse Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaaaaa;'>Real-time Analytics for Roorkee | Weather · Air Quality · Complaints · Forecast</p>", unsafe_allow_html=True)
st.markdown("---")

# ─── SIDEBAR ─────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/3/3d/CSIR-CBRI_Logo.png/200px-CSIR-CBRI_Logo.png", width=120)
st.sidebar.markdown("## ⚙️ Dashboard Controls")
st.sidebar.markdown("**Built by:** Disha Sharma")
st.sidebar.markdown("**Date:** June 2026")
st.sidebar.markdown("---")
show_raw = st.sidebar.checkbox("Show Raw Data Tables", value=False)
chart_theme = st.sidebar.selectbox("Chart Theme", ["plotly_dark", "plotly", "ggplot2", "seaborn"])

# ─── DATA ────────────────────────────────────────────────
import sqlite3

@st.cache_data
def load_data():
    conn = sqlite3.connect("data/city_pulse.db")
    try:
        weather    = pd.read_sql("SELECT * FROM weather_logs", conn)
        air        = pd.read_sql("SELECT * FROM air_quality_logs", conn)
        complaints = pd.read_sql("SELECT * FROM complaints_analysis", conn)
        anomalies  = pd.read_sql("SELECT * FROM weather_anomalies", conn)
        forecast   = pd.read_sql("SELECT * FROM forecast", conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        weather = air = complaints = anomalies = forecast = pd.DataFrame()
    conn.close()
    return weather, air, complaints, anomalies, forecast

weather, air, complaints, anomalies, forecast = load_data()

# ─── AQI FUNCTIONS ───────────────────────────────────────
def calculate_aqi(pm2_5, pm10):
    if pm2_5 <= 30:    aqi_pm25 = (50/30) * pm2_5
    elif pm2_5 <= 60:  aqi_pm25 = 50 + ((50/30) * (pm2_5 - 30))
    elif pm2_5 <= 90:  aqi_pm25 = 100 + ((100/30) * (pm2_5 - 60))
    elif pm2_5 <= 120: aqi_pm25 = 200 + ((100/30) * (pm2_5 - 90))
    elif pm2_5 <= 250: aqi_pm25 = 300 + ((100/130) * (pm2_5 - 120))
    else:              aqi_pm25 = 400 + ((100/130) * (pm2_5 - 250))

    if pm10 <= 50:     aqi_pm10 = pm10
    elif pm10 <= 100:  aqi_pm10 = 50 + (pm10 - 50)
    elif pm10 <= 250:  aqi_pm10 = 100 + ((100/150) * (pm10 - 100))
    elif pm10 <= 350:  aqi_pm10 = 200 + (pm10 - 250)
    elif pm10 <= 430:  aqi_pm10 = 300 + ((100/80) * (pm10 - 350))
    else:              aqi_pm10 = 400 + ((100/80) * (pm10 - 430))

    return round(max(aqi_pm25, aqi_pm10))

def get_aqi_level(aqi):
    if aqi <= 50:    return "Good 🟢"
    elif aqi <= 100: return "Satisfactory 🟡"
    elif aqi <= 200: return "Moderate 🟠"
    elif aqi <= 300: return "Poor 🔴"
    elif aqi <= 400: return "Very Poor 🟣"
    else:            return "Severe ⚫"

# ─── TOP KPI CARDS ───────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    temp = weather['temperature'].iloc[-1] if not weather.empty else "N/A"
    st.metric("🌡️ Temperature", f"{temp}°C")

with col2:
    pm25 = air['pm2_5'].iloc[-1] if not air.empty else 0
    pm10 = air['pm10'].iloc[-1] if not air.empty else 0
    aqi_score = calculate_aqi(pm25, pm10)
    st.metric("🎯 AQI Score", aqi_score)

with col3:
    st.metric("📊 AQI Level", get_aqi_level(aqi_score))

with col4:
    unusual = len(anomalies[anomalies['status'] == 'Unusual']) if not anomalies.empty else 0
    st.metric("🚨 Anomalies", unusual)

with col5:
    if not complaints.empty:
        pos = len(complaints[complaints['sentiment_label'] == 'Positive'])
        pct = round(pos / len(complaints) * 100)
    else:
        pct = 0
    st.metric("😊 Positive %", f"{pct}%")

st.markdown("---")

# ─── TABS ────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🌤️ Weather & Anomalies",
    "💨 Air Quality & AQI",
    "📝 Complaint Sentiment",
    "📈 Temperature Forecast"
])

# ════════════════════════════════════════════════
# TAB 1 — WEATHER
# ════════════════════════════════════════════════
with tab1:
    st.subheader("🌡️ Temperature Trend with Anomalies")

    if not anomalies.empty:
        # Interactive scatter with hover info
        fig1 = px.scatter(
            anomalies,
            x='timestamp', y='temperature',
            color='status',
            size='windspeed',
            hover_data=['windspeed', 'status'],
            title='Temperature Log — Hover over points for details',
            color_discrete_map={'Normal':'#00d4ff', 'Unusual':'#ff4444'},
            template=chart_theme
        )
        fig1.update_traces(marker=dict(line=dict(width=1, color='white')))
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Wind speed line chart
        fig_wind = px.line(
            anomalies, x='timestamp', y='windspeed',
            title='💨 Wind Speed Over Time',
            template=chart_theme,
            markers=True
        )
        fig_wind.update_traces(line_color='#ffaa00', line_width=2)
        fig_wind.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_wind, use_container_width=True)

    if show_raw and not weather.empty:
        st.subheader("Raw Weather Data")
        st.dataframe(weather, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 2 — AIR QUALITY + AQI
# ════════════════════════════════════════════════
with tab2:
    st.subheader("💨 Air Quality Index — Roorkee")

    col1, col2 = st.columns([1, 2])

    with col1:
        # AQI Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi_score,
            title={'text': f"AQI — {get_aqi_level(aqi_score)}", 'font': {'color': 'white', 'size': 16}},
            number={'font': {'color': 'white', 'size': 48}},
            gauge={
                'axis': {'range': [0, 500], 'tickcolor': 'white'},
                'bar': {'color': '#ffffff', 'thickness': 0.25},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 50],    'color': '#00e400'},
                    {'range': [50, 100],  'color': '#ffff00'},
                    {'range': [100, 200], 'color': '#ff7e00'},
                    {'range': [200, 300], 'color': '#ff0000'},
                    {'range': [300, 400], 'color': '#8f3f97'},
                    {'range': [400, 500], 'color': '#7e0023'},
                ],
                'threshold': {
                    'line': {'color': 'white', 'width': 4},
                    'thickness': 0.75,
                    'value': aqi_score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=300
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        if not air.empty:
            # PM2.5 vs PM10 grouped bar
            fig_air = px.bar(
                air, x='timestamp', y=['pm2_5', 'pm10'],
                title='PM2.5 vs PM10 Levels',
                barmode='group',
                template=chart_theme,
                color_discrete_sequence=['#FF9800', '#9C27B0'],
                hover_data=['carbon_monoxide', 'nitrogen_dioxide']
            )
            fig_air.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_air, use_container_width=True)

    # AQI Reference Table
    st.subheader("📋 AQI Reference Guide (India CPCB Standard)")
    aqi_ref = pd.DataFrame({
        "AQI Range":    ["0–50", "51–100", "101–200", "201–300", "301–400", "401–500"],
        "Level":        ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"],
        "Indicator":    ["🟢", "🟡", "🟠", "🔴", "🟣", "⚫"],
        "Health Impact": [
            "Minimal impact",
            "Minor breathing discomfort to sensitive people",
            "Breathing discomfort to asthma patients",
            "Breathing discomfort to most people on prolonged exposure",
            "Respiratory illness on prolonged exposure",
            "Affects healthy people, serious risk to sensitive groups"
        ]
    })
    st.dataframe(aqi_ref, use_container_width=True, hide_index=True)

    if show_raw and not air.empty:
        st.subheader("Raw Air Quality Data")
        st.dataframe(air, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 3 — COMPLAINTS
# ════════════════════════════════════════════════
with tab3:
    st.subheader("📝 Citizen Complaint Sentiment Analysis")

    if not complaints.empty:
        col1, col2 = st.columns(2)

        with col1:
            # Interactive pie chart
            fig_pie = px.pie(
                complaints,
                names='sentiment_label',
                title='Sentiment Distribution',
                template=chart_theme,
                color_discrete_sequence=['#4CAF50', '#F44336', '#9E9E9E'],
                hole=0.4   # donut style
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='%{label}: %{value} complaints<br>%{percent}'
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Horizontal bar chart of scores
            fig_bar = px.bar(
                complaints,
                x='sentiment_score',
                y='complaint',
                color='sentiment_label',
                orientation='h',
                title='Sentiment Score per Complaint',
                template=chart_theme,
                color_discrete_map={
                    'Positive': '#4CAF50',
                    'Negative': '#F44336',
                    'Neutral':  '#9E9E9E'
                }
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Complaints table with color
        st.subheader("All Complaints")
        st.dataframe(complaints, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 4 — FORECAST
# ════════════════════════════════════════════════
with tab4:
    st.subheader("📈 7-Day Temperature Forecast")

    if not forecast.empty:
        # Area chart for forecast
        fig_forecast = go.Figure()

        fig_forecast.add_trace(go.Scatter(
            x=forecast['day'],
            y=forecast['forecasted_temp'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#E91E63', width=3),
            marker=dict(size=10, color='#E91E63', line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor='rgba(233,30,99,0.1)',
            hovertemplate='%{x}<br>Temperature: %{y}°C<extra></extra>'
        ))

        fig_forecast.update_layout(
            title='Roorkee — Next 7 Days Temperature Forecast',
            xaxis_title='Day',
            yaxis_title='Temperature (°C)',
            template=chart_theme,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        # Min Max stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ Min Forecast", f"{forecast['forecasted_temp'].min()}°C")
        with col2:
            st.metric("🌡️ Max Forecast", f"{forecast['forecasted_temp'].max()}°C")
        with col3:
            st.metric("🌡️ Avg Forecast", f"{forecast['forecasted_temp'].mean().round(1)}°C")

        if show_raw:
            st.dataframe(forecast, use_container_width=True, hide_index=True)

# ─── FOOTER ──────────────────────────────────────────────
st.markdown("---")
st.markdown("""
    <p style='text-align:center; color:#555555; font-size:13px;'>
    🏙️ City Smart Pulse | Built by <b>Disha Sharma</b> 
    Data: Open-Meteo API
    </p>
""", unsafe_allow_html=True)