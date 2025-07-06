# app.py
import fredapi 
import streamlit as st
import yfinance as yf
from fredapi import Fred
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Isaura's Macro Dashboard")

# Load secrets
fred = Fred(api_key=st.secrets["fred"]["api_key"])

# FRED: US 10Y Yield
yield_10y = fred.get_series("DGS10")
st.subheader("📉 10-Year Treasury Yield")
st.line_chart(yield_10y)

# YFinance: SPY
spy = yf.download("SPY", period="5d", interval="1h")
st.subheader("📈 SPY (S&P 500 ETF)")
st.line_chart(spy["Close"])

# YFinance: DXY via UUP ETF as a proxy
dxy = yf.download("UUP", period="5d", interval="1h")
st.subheader("💵 Dollar Index (via UUP ETF)")
st.line_chart(dxy["Close"])
