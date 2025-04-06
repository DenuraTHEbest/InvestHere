import pandas as pd
from datetime import datetime, timedelta
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
from ta.trend import MACD
import sys
decimal_value = float(sys.argv[1])  # Gets the decimalValue from Flask
weighted_sentiment = float(sys.argv[2])  # Gets the weighted sentiment from Flask

class FeatureEngineeringPipeline:
    def __init__(self, initial_data_path=None):
        # Initialize with empty DataFrame to store historical data
        self.historical_data = pd.DataFrame(columns=['Date', 'Price_Lag1', 'Weighted_Sentiment'])
        
        # Load initial data if provided
        if initial_data_path:
            self.load_initial_data(initial_data_path)
    
    def load_initial_data(self, file_path):
        try:
            df = pd.read_csv(file_path)
            # Ensure the Date column remains as Unix timestamps (integers)
            if not pd.api.types.is_integer_dtype(df['Date']):
                df['Date'] = pd.to_numeric(df['Date'], errors='coerce').fillna(0).astype(int)
            
            # Sort by date
            df = df.sort_values('Date')
            
            # Store in historical data
            self.historical_data = df[['Date', 'Price_Lag1', 'Weighted_Sentiment']].copy()
            
            print(f"Successfully loaded {len(df)} rows of historical data")
        except Exception as e:
            print(f"Error loading initial data: {e}")

    def add_next_day_data(self, input_csv, new_date, new_price, new_sentiment=None):
        """Add the next day's data to the CSV file with all features."""
        try:
            # Convert new_date to datetime
            new_date = pd.to_datetime(new_date, format="%Y-%m-%d")
            
            # Add one day to the entered date
            next_day = new_date + timedelta(days=1)
            
            # Load the existing data from the CSV file
            existing_data = pd.read_csv(input_csv)
            
            # Ensure the Date column remains as Unix timestamps (integers)
            if not pd.api.types.is_integer_dtype(existing_data['Date']):
                existing_data['Date'] = pd.to_numeric(existing_data['Date'], errors='coerce').fillna(0).astype(int)
            
            # Calculate lagged sentiment and price features
            new_row = {
                'Date': int(next_day.timestamp()),  # Keep as Unix timestamp
                'Weighted_Sentiment': new_sentiment,
                'Lagged_Sentiment_1': existing_data['Weighted_Sentiment'].iloc[-1],
                'Lagged_Sentiment_2': existing_data['Lagged_Sentiment_1'].iloc[-1],
                'Lagged_Sentiment_3': existing_data['Lagged_Sentiment_2'].iloc[-1],
                'Lagged_Sentiment_4': existing_data['Lagged_Sentiment_3'].iloc[-1],
                'Lagged_Sentiment_5': existing_data['Lagged_Sentiment_4'].iloc[-1],
                'Lagged_Sentiment_6': existing_data['Lagged_Sentiment_5'].iloc[-1],
                'Lagged_Sentiment_7': existing_data['Lagged_Sentiment_6'].iloc[-1],
                'Lagged_Sentiment_8': existing_data['Lagged_Sentiment_7'].iloc[-1],
                'Lagged_Sentiment_9': existing_data['Lagged_Sentiment_8'].iloc[-1],
                'Price_Lag1': new_price,
                'Price_Lag2': existing_data['Price_Lag1'].iloc[-1],
                'Price_Lag3': existing_data['Price_Lag2'].iloc[-1],
                'Price_Lag4': existing_data['Price_Lag3'].iloc[-1],
                'Price_Lag5': existing_data['Price_Lag4'].iloc[-1],
                'Price_Lag6': existing_data['Price_Lag5'].iloc[-1],
                'Price_Lag7': existing_data['Price_Lag6'].iloc[-1],
                'Price_Lag8': existing_data['Price_Lag7'].iloc[-1],
                'Price_Lag9': existing_data['Price_Lag8'].iloc[-1],
                'Price_Lag10': existing_data['Price_Lag9'].iloc[-1],
                'Price_Lag12': existing_data['Price_Lag10'].iloc[-2],
                'Price_Lag15': existing_data['Price_Lag12'].iloc[-3],
                'Price_Lag18': existing_data['Price_Lag15'].iloc[-4],
                'Price_Lag20': existing_data['Price_Lag18'].iloc[-5],
                'Price_Lag25': existing_data['Price_Lag20'].iloc[-6],
                'Price_Lag30': existing_data['Price_Lag25'].iloc[-7],
            }
            
            # Append the new row to the existing data
            updated_data = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
            
            # Calculate EMA features using the ta library
            updated_data['EMA_7'] = EMAIndicator(close=updated_data['Price_Lag1'], window=7).ema_indicator()
            updated_data['EMA_14'] = EMAIndicator(close=updated_data['Price_Lag1'], window=14).ema_indicator()
            updated_data['EMA_30'] = EMAIndicator(close=updated_data['Price_Lag1'], window=30).ema_indicator()
            
            # Calculate MACD features
            macd = MACD(close=updated_data['Price_Lag1'])
            updated_data['MACD'] = macd.macd()
            updated_data['MACD_Signal'] = macd.macd_signal()
            updated_data['MACD_Histogram'] = macd.macd_diff()
            
            # Calculate Bollinger Bands features
            bollinger = BollingerBands(close=updated_data['Price_Lag1'], window=20, window_dev=2)
            updated_data['Bollinger_High'] = bollinger.bollinger_hband()
            updated_data['Bollinger_Low'] = bollinger.bollinger_lband()
            updated_data['Bollinger_Width'] = updated_data['Bollinger_High'] - updated_data['Bollinger_Low']
            
            # Write the updated data back to the CSV file
            updated_data.to_csv(input_csv, index=False)
            print(f"Next day's data added and saved to {input_csv}")
        except Exception as e:
            print(f"Error adding next day's data: {e}")
            
# Example usage
input_csv = "aspi_test_features.csv"  # Path to the input CSV file
new_date = "2024-05-16"  # Entered date
new_price = decimal_value  # New price to add
new_sentiment = weighted_sentiment

# Initialize the pipeline and add the next day's data
pipeline = FeatureEngineeringPipeline(initial_data_path=input_csv)
pipeline.add_next_day_data(input_csv, new_date, new_price, new_sentiment)
