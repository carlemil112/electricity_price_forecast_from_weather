import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import pandas as pd



st.title("Danish Electricity Price Forecast")

#Call API
response = requests.get("http://api:8000/forecast")

#Parse
data = response.json()


df = pd.DataFrame(data)

fig = px.line(df, x="timestamp", y="forecast_dkk_mwh",
              title="Next 24 hours",
              labels={"timestamp": "Time (UTC)", "forecast_dkk_mwh": "Price (DKK/MWh)"})

st.plotly_chart(fig)