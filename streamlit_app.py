import streamlit as st
import plotly
import requests
import pandas as pd
import plotly.graph_objs as go
api_key = st.secrets["api_key"]
# Function to get stock data from Alpha Vantage API
def get_stock_data(symbol, interval='daily'):
    # Your Alpha Vantage API key
   
    
    function = 'TIME_SERIES_DAILY' if interval == 'daily' else 'TIME_SERIES_MONTHLY'
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        prices_data = data.get('Time Series (Daily)' if interval == 'daily' else 'Monthly Time Series')
        if prices_data:
            hist_data = pd.DataFrame(prices_data).T
            hist_data.index = pd.to_datetime(hist_data.index)
            hist_data.columns = [col.split()[-1] for col in hist_data.columns]  # Clean column names
            return hist_data
    return None
  
# Function to generate buy/sell signal based on price data
def generate_signal(row):
    if row['close'] > row['open']:
        return 'Buy'
    else:
        return 'Sell'

def create_candlestick_chart(stock_data, symbol, interval='daily'):
    fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                         open=pd.to_numeric(stock_data['open']),
                                         high=pd.to_numeric(stock_data['high']),
                                         low=pd.to_numeric(stock_data['low']),
                                         close=pd.to_numeric(stock_data['close']))])
    fig.update_layout(xaxis_rangeslider_visible=False)  # Remove range slider

    if interval == 'daily':
        # Generate buy/sell signal and sentiment percentage for daily data
        stock_data['signal'] = stock_data.apply(generate_signal, axis=1)
        
        # Calculate sentiment percentage based on opening and closing prices
        stock_data['sentiment_percentage'] = ((pd.to_numeric(stock_data['close']) - pd.to_numeric(stock_data['open'])) / pd.to_numeric(stock_data['open'])) * 100

        # Add buy/sell signal and sentiment percentage as text annotations
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['close'],
                                 mode='text',
                                 text=stock_data.apply(lambda row: f"Sentiment: {row['sentiment_percentage']:.2f}%\nRecommendation: {row['signal']}", axis=1),
                                 textposition="top center",
                                 showlegend=False,
                                 textfont=dict(color='blue')
                                 ))

        # Add buy/sell signal as markers
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['close'],
                                 mode='markers',
                                 marker=dict(color=stock_data['signal'].map({'Buy': 'green', 'Sell': 'red'}),
                                             size=8,
                                             symbol='triangle-up',
                                             opacity=0.8),
                                 name='Buy/Sell Signal'))

        fig.update_layout(title=f'Daily Candlestick Chart for {symbol}',
                          xaxis_title='Date',
                          yaxis_title='Price')

    else:
        fig.update_layout(title=f'Monthly Candlestick Chart for {symbol}',
                          xaxis_title='Date',
                          yaxis_title='Price')

    return fig

# Main Streamlit app
def main():
    st.title("Stock Candlestick Chart")

    # Input stock symbol from the user
    symbol = st.text_input("Enter the stock symbol (e.g., AAPL):")

    # Get daily stock data from Alpha Vantage API
    daily_stock_data = get_stock_data(symbol, 'daily')

    # Get monthly stock data from Alpha Vantage API
    monthly_stock_data = get_stock_data(symbol, 'monthly')

    if daily_stock_data is not None:
        # Create daily candlestick chart
        st.plotly_chart(create_candlestick_chart(daily_stock_data, symbol, 'daily'))

    if monthly_stock_data is not None:
        # Create monthly candlestick chart
        st.plotly_chart(create_candlestick_chart(monthly_stock_data, symbol, 'monthly'))
    else:
        st.error("Failed to retrieve stock data")

if __name__ == "__main__":
    main()
