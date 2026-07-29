import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    calculate_summary,
    asset_summary,
    search_assets,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="PortfolioPilot AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
<style>

.main{
    padding-top:1rem;
}

.stMetric{
    border-radius:10px;
    padding:10px;
}

footer{
    visibility:hidden;
}

</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📈 PortfolioPilot AI")

st.caption(
    "AI-powered Investment Portfolio Dashboard"
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Upload Portfolio Dataset")

st.sidebar.info(
"""
Required CSV columns:

• Date
• Asset
• Quantity
• Buy Price
• Current Price
"""
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
)

# --------------------------------------------------
# Wait for Upload
# --------------------------------------------------

if uploaded_file is None:

    st.info(
        "Upload a CSV file to begin."
    )

    st.stop()

# --------------------------------------------------
# Safe Data Loading
# --------------------------------------------------

try:

    df = load_data(uploaded_file)

except Exception as e:

    st.error(
        "Unable to load dataset."
    )

    st.exception(e)

    st.stop()

# --------------------------------------------------
# Empty Dataset Check
# --------------------------------------------------

if df.empty:

    st.warning(
        "Dataset contains no valid records."
    )

    st.stop()
# --------------------------------------------------
# Portfolio Summary
# --------------------------------------------------

try:

    summary = calculate_summary(df)

except Exception as e:

    st.error(
        "Unable to calculate portfolio summary."
    )

    st.exception(e)

    st.stop()

st.subheader("📊 Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "💰 Total Investment",
        f"₹{summary['Investment']:,.2f}",
    )

with col2:

    st.metric(
        "📈 Current Value",
        f"₹{summary['Current Value']:,.2f}",
    )

with col3:

    st.metric(
        "💹 Profit / Loss",
        f"₹{summary['Profit']:,.2f}",
    )

with col4:

    st.metric(
        "📊 Return %",
        f"{summary['Return %']:.2f}%",
    )

st.divider()

# --------------------------------------------------
# Asset Summary
# --------------------------------------------------

try:

    assets_df = asset_summary(df)

except Exception as e:

    st.error(
        "Unable to generate asset summary."
    )

    st.exception(e)

    assets_df = pd.DataFrame(
        columns=[
            "Asset",
            "Investment",
            "Current Value",
        ]
    )

st.subheader("📦 Portfolio Allocation")

st.dataframe(
    assets_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# Portfolio Statistics
# --------------------------------------------------

st.subheader("📈 Portfolio Statistics")

left, right = st.columns(2)

with left:

    st.write(
        f"**Assets:** {df['Asset'].nunique()}"
    )

    st.write(
        f"**Holdings:** {len(df)}"
    )

with right:

    st.write(
        f"**First Investment:** "
        f"{df['Date'].min().date()}"
    )

    st.write(
        f"**Latest Investment:** "
        f"{df['Date'].max().date()}"
    )

st.divider()
# --------------------------------------------------
# Asset Search
# --------------------------------------------------

st.subheader("🔍 Asset Search")

search_text = st.text_input(
    "Search Asset",
    placeholder="Example: AAPL, TSLA, INFY, BTC",
)

try:

    filtered_df = search_assets(
        df,
        search_text,
    ).reset_index(drop=True)

except Exception as e:

    st.error(
        "Unable to search assets."
    )

    st.exception(e)

    filtered_df = df.copy().reset_index(drop=True)

# --------------------------------------------------
# Portfolio Holdings
# --------------------------------------------------

portfolio_df = filtered_df.copy()

if not portfolio_df.empty:

    portfolio_df["Investment"] = (
        portfolio_df["Quantity"]
        * portfolio_df["Buy Price"]
    )

    portfolio_df["Current Value"] = (
        portfolio_df["Quantity"]
        * portfolio_df["Current Price"]
    )

    portfolio_df["Profit"] = (
        portfolio_df["Current Value"]
        - portfolio_df["Investment"]
    )

st.write(
    f"Showing **{len(portfolio_df):,}** holding(s)."
)

if portfolio_df.empty:

    st.warning(
        "No matching assets found."
    )

else:

    st.dataframe(
        portfolio_df,
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------
# Download Portfolio
# --------------------------------------------------

try:

    csv = portfolio_df.to_csv(
        index=False,
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Portfolio CSV",
        data=csv,
        file_name="portfolio.csv",
        mime="text/csv",
    )

except Exception as e:

    st.error(
        "Unable to prepare CSV download."
    )

    st.exception(e)

st.divider()

# --------------------------------------------------
# Top Holdings
# --------------------------------------------------

st.subheader("🏆 Top Holdings")

if not portfolio_df.empty:

    top_holdings = portfolio_df.sort_values(
        by="Current Value",
        ascending=False,
    ).head(10)

    st.dataframe(
        top_holdings,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No holdings available."
    )

st.divider()

# --------------------------------------------------
# Dataset Preview
# --------------------------------------------------

st.subheader("📄 Dataset Preview")

preview_rows = st.slider(
    "Rows to Preview",
    min_value=5,
    max_value=50,
    value=10,
)

st.dataframe(
    filtered_df.head(preview_rows),
    use_container_width=True,
    hide_index=True,
)

st.divider()
# --------------------------------------------------
# Portfolio Analytics
# --------------------------------------------------

st.subheader("📊 Portfolio Analytics")

# --------------------------------------------------
# Asset Allocation
# --------------------------------------------------

try:

    if not assets_df.empty:

        fig = px.pie(
            assets_df,
            names="Asset",
            values="Current Value",
            hole=0.45,
            title="Portfolio Allocation",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate asset allocation chart."
    )

    st.exception(e)

# --------------------------------------------------
# Investment vs Current Value
# --------------------------------------------------

try:

    if not assets_df.empty:

        fig = px.bar(
            assets_df,
            x="Asset",
            y=[
                "Investment",
                "Current Value",
            ],
            barmode="group",
            title="Investment vs Current Value",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate comparison chart."
    )

    st.exception(e)

# --------------------------------------------------
# Profit / Loss by Asset
# --------------------------------------------------

try:

    profit_df = assets_df.copy()

    profit_df["Profit"] = (
        profit_df["Current Value"]
        - profit_df["Investment"]
    )

    fig = px.bar(
        profit_df,
        x="Asset",
        y="Profit",
        title="Profit / Loss by Asset",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate profit chart."
    )

    st.exception(e)

# --------------------------------------------------
# Current Value Distribution
# --------------------------------------------------

try:

    fig = px.histogram(
        portfolio_df,
        x="Current Value",
        nbins=20,
        title="Current Value Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate distribution chart."
    )

    st.exception(e)

# --------------------------------------------------
# Investment Timeline
# --------------------------------------------------

try:

    timeline_df = (
        filtered_df.copy()
    )

    timeline_df["Investment"] = (
        timeline_df["Quantity"]
        * timeline_df["Buy Price"]
    )

    timeline_df = (
        timeline_df
        .sort_values("Date")
    )

    fig = px.line(
        timeline_df,
        x="Date",
        y="Investment",
        color="Asset",
        markers=True,
        title="Investment Timeline",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate investment timeline."
    )

    st.exception(e)

st.divider()
# --------------------------------------------------
# Asset Insights
# --------------------------------------------------

st.subheader("📈 Asset Insights")

display_df = portfolio_df.reset_index(
    drop=True
)

if display_df.empty:

    st.info(
        "No portfolio assets available."
    )

else:

    selected_index = st.selectbox(
        "Select Asset",
        options=range(len(display_df)),
        format_func=lambda x:
            f"{display_df.iloc[x]['Asset']} | "
            f"₹{display_df.iloc[x]['Current Value']:,.2f}",
    )

    asset = display_df.iloc[selected_index]

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Asset Details")

        st.write(
            f"**Asset:** {asset['Asset']}"
        )

        st.write(
            f"**Quantity:** {asset['Quantity']}"
        )

        st.write(
            f"**Buy Price:** ₹{asset['Buy Price']:,.2f}"
        )

        st.write(
            f"**Current Price:** ₹{asset['Current Price']:,.2f}"
        )

        st.write(
            f"**Investment:** ₹{asset['Investment']:,.2f}"
        )

        st.write(
            f"**Current Value:** ₹{asset['Current Value']:,.2f}"
        )

    with col2:

        st.write("### Performance")

        st.write(
            f"**Profit / Loss:** ₹{asset['Profit']:,.2f}"
        )

        roi = 0.0

        if asset["Investment"] > 0:

            roi = (
                asset["Profit"]
                / asset["Investment"]
            ) * 100

        st.write(
            f"**Return:** {roi:.2f}%"
        )

        average_value = display_df[
            "Current Value"
        ].mean()

        if asset["Current Value"] >= average_value * 2:

            st.success(
                "This is one of your largest holdings."
            )

        elif asset["Current Value"] >= average_value:

            st.info(
                "This holding is above your portfolio average."
            )

        else:

            st.warning(
                "This holding is below your portfolio average."
            )

st.divider()

# --------------------------------------------------
# Top Performing Assets
# --------------------------------------------------

st.subheader("🏆 Top Performing Assets")

ranking_df = display_df.sort_values(
    by="Profit",
    ascending=False,
)

st.dataframe(
    ranking_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()
# --------------------------------------------------
# Dataset Health Report
# --------------------------------------------------

st.subheader("🩺 Dataset Health Report")

total_records = len(df)

missing_values = int(df.isna().sum().sum())

duplicate_rows = int(df.duplicated().sum())

invalid_quantity = int((df["Quantity"] <= 0).sum())

invalid_prices = int(
    (
        (df["Buy Price"] <= 0)
        |
        (df["Current Price"] <= 0)
    ).sum()
)

health_score = max(
    0,
    100
    - (
        missing_values
        + duplicate_rows
        + invalid_quantity
        + invalid_prices
    ),
)

health_score = min(100, health_score)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Records",
        total_records,
    )

    st.metric(
        "Missing Values",
        missing_values,
    )

with col2:

    st.metric(
        "Duplicate Rows",
        duplicate_rows,
    )

    st.metric(
        "Invalid Quantity",
        invalid_quantity,
    )

with col3:

    st.metric(
        "Invalid Prices",
        invalid_prices,
    )

    st.metric(
        "Dataset Quality",
        f"{health_score}%",
    )

st.divider()

# --------------------------------------------------
# Portfolio Summary
# --------------------------------------------------

st.subheader("📋 Portfolio Summary")

summary_df = pd.DataFrame(
    {
        "Metric": [
            "Rows",
            "Columns",
            "Assets",
            "Total Investment",
            "Current Value",
            "Profit / Loss",
            "Return %",
        ],
        "Value": [
            len(df),
            len(df.columns),
            df["Asset"].nunique(),
            f"₹{summary['Investment']:,.2f}",
            f"₹{summary['Current Value']:,.2f}",
            f"₹{summary['Profit']:,.2f}",
            f"{summary['Return %']:.2f}%",
        ],
    }
)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "PortfolioPilot AI • Built with Streamlit, Pandas and Plotly"
)

















