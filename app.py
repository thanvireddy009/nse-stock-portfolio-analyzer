import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# PAGE CONFIG
st.set_page_config(
    page_title="NSE Portfolio Analyzer",
    page_icon="📈",
    layout="wide"
)

# CUSTOM CSS
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
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

</style>
""", unsafe_allow_html=True)

# TITLE
st.title("📈 NSE Stock Portfolio Analyzer")

st.write("Analyze live NSE stock data, technical indicators, and company financials.")

# NIFTY 50 STOCKS
example_stocks = [
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

# SIDEBAR
st.sidebar.header("🔍 Search Stock")

selected = st.sidebar.selectbox(
    "Choose NIFTY 50 Company",
    example_stocks
)

custom_stock = st.sidebar.text_input(
    "Or Enter NSE Symbol",
    selected
)

# FORMAT STOCK SYMBOL
stock = custom_stock.upper()

if not stock.endswith(".NS"):
    stock += ".NS"

# HELPER FUNCTIONS
def safe_get(value):

    if value is None:
        return "Data Not Available"

    return value

def format_crore(value):

    if isinstance(value, (int, float)):

        value = value / 10000000

        return f"₹ {value:,.2f} Cr"

    return value

# FETCH DATA
if stock:

    with st.spinner("Fetching market data..."):

        try:

            company = yf.Ticker(stock)

            info = company.info

            # COMPANY INFO
            company_name = safe_get(info.get("longName"))
            current_price = safe_get(info.get("currentPrice"))
            pe_ratio = safe_get(info.get("trailingPE"))
            roe = safe_get(info.get("returnOnEquity"))
            debt_equity = safe_get(info.get("debtToEquity"))
            net_margin = safe_get(info.get("profitMargins"))

            st.subheader(company_name)

            # METRICS
            metrics = {
                "Current Price": current_price,
                "P/E Ratio": pe_ratio,
                "ROE": roe,
                "Debt to Equity": debt_equity,
                "Net Profit Margin": net_margin
            }

            for key, value in metrics.items():

                st.markdown(f"""
                <div class="metric-card">
                    <h3>{key}</h3>
                    <h2>{value}</h2>
                </div>
                """, unsafe_allow_html=True)

            # STOCK HISTORY
            st.subheader("📊 Stock Price Analysis")

            history = company.history(period="1y")

            # MOVING AVERAGES
            history["20 Day MA"] = history["Close"].rolling(window=20).mean()
            history["50 Day MA"] = history["Close"].rolling(window=50).mean()
            history["100 Day MA"] = history["Close"].rolling(window=100).mean()

            # PLOTLY CHART
            fig = go.Figure()

            # CLOSE PRICE
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["Close"],
                mode='lines',
                name='Close Price',
                line=dict(color='cyan', width=3)
            ))

            # 20 MA
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["20 Day MA"],
                mode='lines',
                name='20 Day MA',
                line=dict(color='lime', width=2)
            ))

            # 50 MA
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["50 Day MA"],
                mode='lines',
                name='50 Day MA',
                line=dict(color='orange', width=2)
            ))

            # 100 MA
            fig.add_trace(go.Scatter(
                x=history.index,
                y=history["100 Day MA"],
                mode='lines',
                name='100 Day MA',
                line=dict(color='red', width=2)
            ))

            fig.update_layout(
                template="plotly_dark",
                height=600,
                xaxis_title="Date",
                yaxis_title="Stock Price",
                legend_title="Indicators"
            )

            st.plotly_chart(fig, use_container_width=True)

            # QUARTERLY RESULTS
            st.subheader("📅 Quarterly Financial Results")

            quarterly = company.quarterly_financials

            if not quarterly.empty:

                quarterly = quarterly.map(format_crore)

                st.dataframe(quarterly)

            else:

                st.warning("Quarterly data unavailable.")

            # ANNUAL RESULTS
            st.subheader("📈 Annual Financial Results")

            financials = company.financials

            if not financials.empty:

                financials = financials.map(format_crore)

                st.dataframe(financials)

            else:

                st.warning("Annual financial data unavailable.")

        except Exception as e:

            st.error("Could not fetch stock data.")

            st.write(e)