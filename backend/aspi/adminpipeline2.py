import sys
import pandas as pd
import joblib
import requests
import numpy as np
from datetime import datetime

def log_message(message):
    """Helper function for consistent logging"""
    print(message, file=sys.stderr)
    sys.stderr.flush()  # Ensure immediate output

def main():
    try:
        log_message("\n=== Admin Pipeline Started ===")
        
        # 1. Load model and data
        log_message("Loading model and data...")
        model = joblib.load('./aspi_forecast_model_new.pkl')
        new_test_data = pd.read_csv('./aspi_test_features.csv')
        log_message(f"Model loaded: {type(model)}")
        log_message(f"Data shape: {new_test_data.shape}")
        
        # 2. Predict and get single value
        y_pred = model.predict(new_test_data)
        log_message(f"Raw prediction shape: {y_pred.shape}")
        
        # Handle 2D array output
        if len(y_pred.shape) == 2:
            y_pred = float(y_pred[-1, -1])  # Last element of last prediction
        else:
            y_pred = float(y_pred[-1])  # Last prediction if 1D
            
        log_message(f"Final prediction value: {y_pred}")
        
        # 3. Get decimal_value from command line
        decimal_value = float(sys.argv[1])
        log_message(f"Input value: {decimal_value}")
        
        # 4. Fetch and update predictions
        try:
            log_message("Fetching latest predictions...")
            response = requests.get(
                "http://127.0.0.1:5050/api/get_predictions",
                timeout=5
            )
            response.raise_for_status()
            
            predictions = response.json()
            if not predictions:
                log_message("❌ No predictions found in database")
                sys.exit(1)
                
            # Get most recent date
            latest_date = predictions[0]["Date"]
            log_message(f"Latest date in DB: {latest_date}")
            
            # Prepare update data
            update_data = {
                "Date": latest_date,
                "Predicted_Day_1": y_pred,
                "Actual_Day_1": decimal_value
            }
            
            log_message(f"Sending update: {update_data}")
            update_response = requests.post(
                "http://127.0.0.1:5050/api/update_prediction",
                json=update_data,
                timeout=5
            )
            update_response.raise_for_status()
            
            log_message("✅ Update successful")
            print(y_pred)  # This output is captured by Flask
            
        except requests.exceptions.RequestException as e:
            log_message(f"❌ API Error: {str(e)}")
            if hasattr(e, 'response'):
                log_message(f"Response: {e.response.text}")
            sys.exit(1)
            
    except Exception as e:
        log_message(f"❌ Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()