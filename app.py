import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time


st.set_page_config(
    page_title="NSE Portfolio Analyzer",
    page_icon="NSE(NIFTY50)",
    layout="wide"
)


st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

h1, h2, h3 {
    color: white;
}

.metric-card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    color: white;
}
</style>
""", unsafe_allow_html=True)


st.title("NSE Stock Portfolio Analyzer")
st.write("Analyze live NSE stock data, technical indicators, and risk metrics.")


stocks = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT",
    "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BEL", "BHARTIARTL", "BPCL", "BRITANNIA",
    "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT",
    "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK",
    "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR",
    "ICICIBANK", "INDUSINDBK", "INFY", "ITC",
    "JIOFIN", "JSWSTEEL", "KOTAKBANK", "LT",
    "M&M", "MARUTI", "NESTLEIND", "NTPC",
    "ONGC", "POWERGRID", "RELIANCE", "SBILIFE",
    "SBIN", "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM",
    "TATAMOTORS", "TATASTEEL", "TCS", "TECHM",
    "TITAN", "TRENT", "ULTRACEMCO", "WIPRO"
]


st.sidebar.header("🔍 Search Stock")

selected = st.sidebar.selectbox("Choose NSE Stock", stocks)
custom = st.sidebar.text_input("Or Enter NSE Symbol", selected)

stock = custom.upper()

if not stock.endswith(".NS"):
    stock += ".NS"


# ---------------- SAFE CR FORMAT (FIXED) ----------------
def format_cr(value):
    try:
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value / 1e7:,.2f} Cr"
        return value
    except:
        return "N/A"


if stock:

    with st.spinner("Fetching stock data..."):

        try:
            company = yf.Ticker(stock)

            # retry history
            for i in range(3):
                try:
                    history = company.history(period="1y")
                    if not history.empty:
                        break
                except:
                    time.sleep(2)
            else:
                st.error("Failed to fetch stock data.")
                st.stop()

            # ---------------- FUNDAMENTALS ----------------
            info = {}
            try:
                info = company.info
            except:
                info = {}

            def safe(v):
                if v is None:
                    return "N/A"
                if isinstance(v, (int, float)):
                    return round(v, 2)
                return v

            pe_ratio = safe(info.get("trailingPE"))
            roe = safe(info.get("returnOnEquity"))
            debt_equity = safe(info.get("debtToEquity"))
            net_margin = safe(info.get("profitMargins"))

            current_price = history["Close"].iloc[-1]

            st.subheader(stock)

            col1, col2 = st.columns(2)
            col1.metric("Current Price", f"₹ {current_price:.2f}")
            col2.metric("P/E Ratio", pe_ratio)

            st.metric("ROE", roe)
            st.metric("Debt to Equity", debt_equity)
            st.metric("Net Profit Margin", net_margin)

            # ---------------- TECHNICALS ----------------
            history["20 MA"] = history["Close"].rolling(20).mean()
            history["50 MA"] = history["Close"].rolling(50).mean()
            history["100 MA"] = history["Close"].rolling(100).mean()

            history["Daily Return"] = history["Close"].pct_change()

            volatility = history["Daily Return"].std() * (252 ** 0.5)
            cumulative_return = (history["Close"].iloc[-1] / history["Close"].iloc[0]) - 1

            col2.metric("Cumulative Return", f"{cumulative_return:.2%}")
            st.metric("Annualized Volatility", f"{volatility:.2%}")

            # ---------------- CHART ----------------
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["Close"],
                name="Close Price"
            ))

            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["20 MA"],
                name="20 MA"
            ))

            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["50 MA"]
            ))

            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["100 MA"]
            ))

            fig.update_layout(
                template="plotly_dark",
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

            # ---------------- FINANCIALS (FIXED ₹ CR) ----------------
            st.subheader("Financial Data (₹ Cr)")

            quarterly = company.quarterly_financials
            annual = company.financials

            if quarterly is not None and not quarterly.empty:
                st.write("Quarterly Financials")
                st.dataframe(quarterly.map(format_cr))

            if annual is not None and not annual.empty:
                st.write("Annual Financials")
                st.dataframe(annual.map(format_cr))

        except Exception as e:
            st.error("Could not fetch stock data.")
            st.write(e)