from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import numpy as np
from pymongo import MongoClient
import certifi
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow CORS if frontend is on a different port

# ----------------------------------------------------------------
# 1) MongoDB Configuration
# ----------------------------------------------------------------
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["IndividualDB2"]
collection = db["Compnay_Predictions3"]
print("✅ Connected to MongoDB Atlas successfully!")

# ----------------------------------------------------------------
# 2) Load Your Trained Model
# ----------------------------------------------------------------
MODEL_PATH = '/backend/company/20daysModel.pkl'
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
else:
    model = None
    print("⚠️ No model file found at", MODEL_PATH)

# ----------------------------------------------------------------
# 3) Feature Definition
# ----------------------------------------------------------------
# Your model expects 12 "base" features, including 'Day' instead of 'Date'
base_features = [
    'Year', 'Month', 'Day',          # Replacing 'Date' with 'Day'
    'RSI_14', 'MACD_Line', 'MACD_Signal', 'MACD_Hist',
    'BB_Mid', 'BB_Upper', 'BB_Lower',
    'Volume_Change', 'ATR_14'
]

# 30 lag features + 3 MAs
optional_features = [f'CLOSE PRICE (Lag {i})' for i in range(1, 31)] + ['MA_7', 'MA_14', 'MA_30']
all_features = base_features + optional_features  # Total of 12 + 33 = 45 features

# ----------------------------------------------------------------
# 4) Primary Endpoint - Analyze & Store Predictions
# ----------------------------------------------------------------
@app.route('/analyze_data', methods=['POST'])
def analyze_data():
    """
    1) Receives a CSV with a "SHORT NAME" column for companies.
    2) CSV may have a "Date" column (string/datetime) which we parse into Year, Month, Day columns.
    3) We group by "SHORT NAME", sort by [Year, Month, Day], take the last row for each company.
    4) We perform a 20-day iterative forecast and store results in MongoDB
       using fields that match the frontend's expectations:
         - "Company_Name", "Date", "Actual_Final"
         - "Predicted_Day_1" ... "Predicted_Day_20"
    5) Returns the predictions as JSON.
    """
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No CSV file was provided.'
        }), 400

    file = request.files['file']

    try:
        # ----------------------------------------------------------------
        # (A) Read the CSV, Clean Column Names
        # ----------------------------------------------------------------
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        # If there's a "Date" column, parse it to create Year, Month, Day
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Day'] = df['Date'].dt.day
            if 'Year' not in df.columns:
                df['Year'] = df['Date'].dt.year
            if 'Month' not in df.columns:
                df['Month'] = df['Date'].dt.month

        # ----------------------------------------------------------------
        # (B) Check for Missing Columns
        # ----------------------------------------------------------------
        missing_cols = [col for col in all_features if col not in df.columns]
        if missing_cols:
            return jsonify({
                'status': 'error',
                'message': f'Missing required columns: {missing_cols}'
            }), 400

        # ----------------------------------------------------------------
        # (C) Group by "SHORT NAME" & Sort
        # ----------------------------------------------------------------
        if 'SHORT NAME' not in df.columns:
            return jsonify({
                'status': 'error',
                'message': 'CSV must contain a "SHORT NAME" column.'
            }), 400

        grouped = df.groupby('SHORT NAME', sort=False)
        all_predictions = {}
        records_to_insert = []  # For MongoDB documents

        # ----------------------------------------------------------------
        # (D) Iterate Over Each Company
        # ----------------------------------------------------------------
        for company, group_data in grouped:
            # Sort by [Year, Month, Day] to ensure last row is the latest
            group_data = group_data.sort_values(by=['Year', 'Month', 'Day'])
            last_row = group_data.tail(1)

            # Build a final date string
            if 'Date' in last_row.columns:
                final_date_val = str(last_row['Date'].values[0])  # raw date
            else:
                y = int(last_row['Year'].values[0])
                m = int(last_row['Month'].values[0])
                d = int(last_row['Day'].values[0])
                final_date_val = f"{y}-{m:02d}-{d:02d}"

            # Retrieve some "actual" price for Day 0
            # If your CSV has a specific column for the final actual price, 
            # substitute it here. For example, 'CLOSE PRICE':
            if 'CLOSE PRICE' in last_row.columns:
                actual_final = float(last_row['CLOSE PRICE'].values[0])
            else:
                # If not available, store None or 0
                actual_final = None

            # ----------------------------------------------------------------
            # (E) Predict 20 Days Ahead
            # ----------------------------------------------------------------
            if model is None:
                predictions = [0]*20
            else:
                initial_features = last_row[all_features].values[0]
                current_features = initial_features.copy()
                predictions = []

                # Indices: 0-11 => base features, 12-41 => 30 lags, 42-44 => MAs
                lag_start = 12
                lag_end   = 42

                for _ in range(20):
                    X_input = pd.DataFrame([current_features], columns=all_features)
                    pred = model.predict(X_input)[0]
                    predictions.append(float(pred))

                    # Shift lags
                    new_lags = np.concatenate(([pred], current_features[lag_start:lag_end-1]))
                    current_features[lag_start:lag_end] = new_lags

                    # Recalculate MAs
                    ma7  = np.mean(current_features[lag_start:lag_start+7])
                    ma14 = np.mean(current_features[lag_start:lag_start+14])
                    ma30 = np.mean(current_features[lag_start:lag_end])
                    current_features[42] = ma7
                    current_features[43] = ma14
                    current_features[44] = ma30

            # ----------------------------------------------------------------
            # (F) Store Predictions in Memory & Prepare MongoDB Record
            #     in a shape that matches the Next.js code
            # ----------------------------------------------------------------
            doc_for_db = {
                "Company_Name": company,    # rename "SHORT NAME" -> "Company_Name"
                "Date": final_date_val,
                "Actual_Final": actual_final,
                "Timestamp": datetime.now().isoformat()
            }

            # Add "Predicted_Day_1" through "Predicted_Day_20"
            for i, value in enumerate(predictions, start=1):
                doc_for_db[f"Predicted_Day_{i}"] = value

            records_to_insert.append(doc_for_db)
            # For the in-memory dictionary that returns to client now:
            # all_predictions[company] = predictions
            # But we'll store more explicit structure:
            all_predictions[company] = {
                "Date": final_date_val,
                "Actual_Final": actual_final,
                "Predictions": predictions
            }

        # ----------------------------------------------------------------
        # (G) Insert into MongoDB
        # ----------------------------------------------------------------
        if records_to_insert:
            collection.insert_many(records_to_insert)
            print(f"✅ Inserted {len(records_to_insert)} prediction records into MongoDB.")

        # ----------------------------------------------------------------
        # (H) Return JSON Response
        # ----------------------------------------------------------------
        return jsonify({
            'status': 'success',
            'message': 'Analysis completed successfully',
            'predictions': all_predictions
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing file: {str(e)}'
        }), 500

# ----------------------------------------------------------------
# 5) New GET Endpoint: Retrieve All Predictions
# ----------------------------------------------------------------
@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """
    Fetch all documents from the 'Compnay_Predictions2' collection
    and return them as a JSON array. Each doc has:
      - "Company_Name"
      - "Date"
      - "Actual_Final"
      - "Predicted_Day_1" ... "Predicted_Day_20"
      - "Timestamp"
    """
    cursor = collection.find({})
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        results.append(doc)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
