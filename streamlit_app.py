import streamlit as st
from streamlit_autorefresh import st_autorefresh
from fetchers import get_stock_quote, get_stock_yfinance, get_stock_history, get_crypto_price, get_twitter_metrics, push_to_powerbi
from data.db import init_db, simulate_new_orders, get_sales_kpis
import time
from data.db import get_orders
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Live KPI Dashboard", layout="wide")

init_db()

# Auto-refresh every 10s (10000 ms)
count = st_autorefresh(interval=10000, limit=0, key="kpi-refresh")

st.title("Live KPI Dashboard — Demo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.header("E-commerce")
    simulate_new_orders(n=2)
    sales = get_sales_kpis(window_minutes=60)
    st.metric("Total (60m)", f"${sales['total_sales']}")
    st.metric("Orders (60m)", sales['orders'])
    st.metric("Avg Order", f"${sales['avg_order_value']}")
    # show a time series of recent sales
    orders = get_orders(window_hours=24)
    if orders:
        df = pd.DataFrame(orders, columns=["created_at", "amount"] )
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.set_index('created_at').resample('1H').sum().fillna(0)
        st.subheader("Sales (last 24h)")
        st.line_chart(df['amount'])
    else:
        st.info("No orders yet; simulator will create orders on refresh.")

with col2:
    st.header("Stocks")
    api_choice = st.selectbox("Stocks API", ["Alpha Vantage", "yfinance"], key="stocks-api")
    symbol = st.text_input("Symbol", "AAPL", key="stock-symbol")
    if api_choice == "yfinance":
        stock = get_stock_yfinance(symbol)
    else:
        stock = get_stock_quote(symbol)
    if stock.get("error"):
        st.warning(stock['error'])
    else:
        change = stock.get('change')
        st.metric(f"{stock['symbol']}", f"${stock['price']}", f"{change}")
    # stock historical chart
    with st.expander("Show historical trend"):
        hist = get_stock_history(symbol, period="7d", interval="1h")
        if hist.get('error'):
            st.info(hist['error'])
        else:
            s_df = pd.DataFrame({'timestamp': hist['timestamps'], 'close': hist['prices']})
            s_df['timestamp'] = pd.to_datetime(s_df['timestamp'])
            s_df = s_df.set_index('timestamp')
            st.line_chart(s_df['close'])

with col3:
    st.header("Crypto")
    crypto = get_crypto_price("bitcoin")
    if crypto.get("error"):
        st.warning(crypto['error'])
    else:
        st.metric(crypto['coin'], f"${crypto['price']}")

with col4:
    st.header("Social")
    tw = get_twitter_metrics("twitter")
    if tw.get("error"):
        st.info("Twitter creds missing or rate-limited")
    else:
        st.write(tw)

st.markdown("---")

st.header("KPI Streams")
st.write("Use the push helper to send selected KPI payloads to Power BI or other streaming sinks.")

if st.button("Push sales KPIs to Power BI"):
    payload = [{
        "timestamp": time.time(),
        "total_sales": sales['total_sales'],
        "orders": sales['orders'],
        "avg_order_value": sales['avg_order_value']
    }]
    res = push_to_powerbi(payload)
    st.write(res)

st.markdown("\n\nBuilt-in simulator: new orders insert on refresh. Add APIs and Power BI URL in .env to enable live feeds.")
