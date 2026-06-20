import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="City Smart Pulse — Roorkee",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ City Smart Pulse Dashboard")
st.markdown("**Real-time Analytics for Roorkee | Weather · Air Quality · Complaints**")
st.markdown("---")

# ---- DATA (hardcoded for deployment) ----

weather = pd.DataFrame({
    "timestamp": ["2024-06-01","2024-06-02","2024-06-03","2024-06-04","2024-06-05"],
    "temperature": [32.1, 34.5, 31.2, 35.8, 33.0],
    "windspeed": [12.0, 8.5, 15.2, 6.0, 10.5],
    "city": ["Roorkee"] * 5
})

air = pd.DataFrame({
    "timestamp": ["2024-06-01","2024-06-02","2024-06-03","2024-06-04","2024-06-05"],
    "pm2_5": [85.2, 92.1, 78.5, 95.0, 88.3],
    "pm10": [120.5, 135.2, 110.8, 140.1, 125.6],
    "carbon_monoxide": [0.8, 1.2, 0.6, 1.5, 0.9],
    "nitrogen_dioxide": [22.5, 28.3, 19.8, 31.2, 24.6],
    "city": ["Roorkee"] * 5
})

complaints = pd.DataFrame({
    "complaint": [
        "Water supply cut for 3 days",
        "Roads excellent after repair",
        "Garbage not collected since Monday",
        "Street lights working perfectly",
        "Electricity goes off every evening",
        "New park is beautiful",
        "Drainage system is blocked",
        "Bus service is punctual"
    ],
    "sentiment_score": [-0.4, 0.7, -0.6, 0.8, -0.3, 0.9, -0.5, 0.6],
    "sentiment_label": [
        "Negative","Positive","Negative","Positive",
        "Negative","Positive","Negative","Positive"
    ]
})

anomalies = pd.DataFrame({
    "timestamp": [f"2024-06-{i+1:02d}" for i in range(32)],
    "temperature": [32,34,31,35,33,32,34,31,35,33,32,34,31,35,33,
                   32,34,31,35,33,32,34,31,35,33,32,34,31,35,33,65,10],
    "windspeed": [12,8,15,6,10,12,8,15,6,10,12,8,15,6,10,
                 12,8,15,6,10,12,8,15,6,10,12,8,15,6,10,5,95],
    "status": ["Normal"]*30 + ["Unusual","Unusual"]
})

forecast = pd.DataFrame({
    "day": [f"Day +{i}" for i in range(1, 8)],
    "forecasted_temp": [33.2, 34.1, 32.8, 35.5, 33.9, 34.7, 32.1]
})

# ---- KPI CARDS ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌡️ Current Temp", f"{weather['temperature'].iloc[-1]}°C")
with col2:
    st.metric("💨 PM2.5 Level", f"{air['pm2_5'].iloc[-1]} µg/m³")
with col3:
    st.metric("🚨 Anomalies", len(anomalies[anomalies['status'] == 'Unusual']))
with col4:
    pos = len(complaints[complaints['sentiment_label'] == 'Positive'])
    st.metric("😊 Positive %", f"{round(pos/len(complaints)*100)}%")

st.markdown("---")

# ---- TABS ----
tab1, tab2, tab3, tab4 = st.tabs([
    "🌤️ Weather",
    "💨 Air Quality",
    "📝 Complaints",
    "📈 Forecast"
])

with tab1:
    st.subheader("Temperature Log with Anomalies")
    fig1 = px.scatter(
        anomalies, x='timestamp', y='temperature',
        color='status',
        title='Temperature — Anomalies Highlighted',
        color_discrete_map={'Normal':'#2196F3','Unusual':'#F44336'}
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.dataframe(weather, use_container_width=True)

with tab2:
    st.subheader("PM2.5 and PM10 Levels")
    fig2 = px.bar(
        air, x='timestamp', y=['pm2_5','pm10'],
        title='Air Quality — Roorkee',
        barmode='group',
        color_discrete_sequence=['#FF9800','#9C27B0']
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(air, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.pie(
            complaints, names='sentiment_label',
            title='Sentiment Distribution',
            color_discrete_sequence=['#4CAF50','#F44336','#9E9E9E']
        )
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        fig4 = px.bar(
            complaints, x='sentiment_label', y='sentiment_score',
            color='sentiment_label',
            title='Sentiment Scores',
            color_discrete_sequence=['#4CAF50','#F44336']
        )
        st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(complaints, use_container_width=True)

with tab4:
    fig5 = px.line(
        forecast, x='day', y='forecasted_temp',
        title='7-Day Temperature Forecast',
        markers=True
    )
    fig5.update_traces(line_color='#E91E63', line_width=3)
    st.plotly_chart(fig5, use_container_width=True)
    st.dataframe(forecast, use_container_width=True)

st.markdown("---")
st.caption("Built by Disha Sharma | City Smart Pulse |")