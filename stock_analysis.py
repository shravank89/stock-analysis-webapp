import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta


def calculate_moving_average(data, window):
    """Calculate simple moving average"""
    ma = []
    for i in range(len(data)):
        if i < window:
            ma.append(sum(data[:i + 1]) / (i + 1))
        else:
            ma.append(sum(data[i - window + 1:i + 1]) / window)
    return ma


def analyze_indian_stock(symbol, months=12):
    """Analyze Indian stocks with basic technical indicators"""
    try:
        # Add .NS suffix if not present
        if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
            symbol = f"{symbol}.NS"

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        # Fetch stock data
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)

        if len(df) == 0:
            st.warning(f"No data found for {symbol} on NSE. Trying BSE...")
            symbol = symbol.replace('.NS', '.BO')
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)

            if len(df) == 0:
                raise Exception("No data available for either NSE or BSE")

        # Calculate moving averages
        close_prices = df['Close'].values
        volumes = df['Volume'].values

        # Calculate 50-day and 200-day moving averages
        ma50 = calculate_moving_average(close_prices, 50)
        ma200 = calculate_moving_average(close_prices, 200)

        # Analysis results
        analysis = {
            'stock_info': {
                'Symbol': symbol,
                'Exchange': 'NSE' if symbol.endswith('.NS') else 'BSE',
                'Trading Days': len(close_prices)
            },
            'price_metrics': {
                'Current Price': close_prices[-1],
                'High': max(close_prices),
                'Low': min(close_prices),
                'Average Price': sum(close_prices) / len(close_prices),
                'Price Range %': ((max(close_prices) - min(close_prices)) / min(close_prices)) * 100
            },
            'volume_metrics': {
                'Average Volume': sum(volumes) / len(volumes),
                'Max Volume': max(volumes),
                'Last Volume': volumes[-1]
            },
            'technical_indicators': {
                'Current vs 50MA': 'Above' if close_prices[-1] > ma50[-1] else 'Below',
                'Current vs 200MA': 'Above' if close_prices[-1] > ma200[-1] else 'Below',
                '50MA Value': ma50[-1],
                '200MA Value': ma200[-1]
            }
        }

        return analysis, df

    except Exception as e:
        st.error(f"Error analyzing {symbol}: {str(e)}")
        return None, None


def main():
    st.set_page_config(page_title="Indian Stock Analysis", layout="wide")

    # Title and description
    st.title("📈 Indian Stock Market Analysis")
    st.markdown("Enter a stock symbol to analyze its performance")

    # Input section
    col1, col2 = st.columns([2, 1])
    with col1:
        stock_symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE, TCS, HDFCBANK)").upper()
    with col2:
        months = st.slider("Months of Historical Data", min_value=1, max_value=60, value=12)

    # Popular stocks suggestions
    st.markdown("**Popular Stocks:** RELIANCE, TCS, HDFCBANK, INFY, SUNFLAG")

    if stock_symbol:
        # Add a spinner while processing
        with st.spinner(f'Analyzing {stock_symbol}...'):
            analysis, df = analyze_indian_stock(stock_symbol, months)

            if analysis and df is not None:
                # Create three columns for different metrics
                col1, col2, col3 = st.columns(3)

                # Stock Info
                with col1:
                    st.subheader("Stock Information")
                    for key, value in analysis['stock_info'].items():
                        st.write(f"**{key}:** {value}")

                # Price Metrics
                with col2:
                    st.subheader("Price Metrics")
                    for key, value in analysis['price_metrics'].items():
                        if isinstance(value, float):
                            st.write(f"**{key}:** ₹{value:,.2f}")
                        else:
                            st.write(f"**{key}:** {value}")

                # Technical Indicators
                with col3:
                    st.subheader("Technical Indicators")
                    for key, value in analysis['technical_indicators'].items():
                        if isinstance(value, float):
                            st.write(f"**{key}:** ₹{value:,.2f}")
                        else:
                            st.write(f"**{key}:** {value}")

                # Volume Metrics
                st.subheader("Volume Metrics")
                for key, value in analysis['volume_metrics'].items():
                    st.write(f"**{key}:** {value:,.0f}")

                # Display charts
                st.subheader("Price Chart")
                st.line_chart(df['Close'])

                st.subheader("Volume Chart")
                st.bar_chart(df['Volume'])


if __name__ == "__main__":
    main()