

from io import BytesIO
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os

# List of stock symbols 
stock_symbols = ['GRAVITA.NS', 'MAZDOCK.NS', 'ANANTRAJ.NS', 'M&M.NS', 'LODHA.NS', 'BALUFORGE.NS', 
                 'TITAGARH.NS', 'HBLPOWER.NS', 'HAL.NS', 'APARINDS.NS', 'KPIGREEN.NS', 'SENCO.NS', 
                 'ACE.NS', 'POWERMECH.NS', 'PHOENIXLTD.NS', 'BLS.NS', 'AGARIND.NS', 'EKI.NS', 
                 'CAPLIPOINT.NS', 'WABAG.NS', 'NH.NS', 'EMSLIMITED.NS', 'ITDCEM.NS', 'RECLTD.NS', 
                 'LTFOODS.NS']

# Defining the date range for the last 3 months
start_date = "2024-07-05"
end_date = "2024-10-05"

# Create a directory to save the plots
output_dir = "stock_charts"
os.makedirs(output_dir, exist_ok=True)

all_stocks_data = pd.DataFrame()

# Loop through each stock symbol and fetching the historical data
for stock in stock_symbols:
    stock_data = yf.download(stock, start=start_date, end=end_date)
    stock_data['Stock'] = stock  # Add a column for the stock symbol
    all_stocks_data = pd.concat([all_stocks_data, stock_data])

all_stocks_data.reset_index(inplace=True)



# Plotting and saving stock prices for each stock
for stock in stock_symbols:
    stock_data = all_stocks_data[all_stocks_data['Stock'] == stock]
    plt.figure(figsize=(10, 6))
    plt.plot(stock_data['Date'], stock_data['Close'], label=f'{stock} Price')
    plt.title(f'{stock} Stock Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = os.path.join(output_dir, f'{stock}.png')
    plt.savefig(filename)
    plt.close()
