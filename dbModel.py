import os
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Secure MongoDB Atlas Connection
MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/{os.getenv('MONGO_DB')}?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
    db = client[os.getenv("MONGO_DB")]
    company_collection = db["companies"]
    predictions_collection = db["predictions"]
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")

# Flask App
app = Flask(__name__)

# Directories
UPLOAD_FOLDER = r'\preprocessed'
RESULTS_FOLDER = r'\NewResults'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    company_name = os.path.splitext(file.filename)[0]
    df = pd.read_excel(file_path)

    # Process Trading Date
    if 'TRADING DATE' in df.columns:
        df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'])
        df['Year'] = df['TRADING DATE'].dt.year
        df['Month'] = df['TRADING DATE'].dt.month
        df['Day'] = df['TRADING DATE'].dt.day
    else:
        df['Year'], df['Month'], df['Day'] = [None] * 3

    # Select only features available before market close
    features = [col for col in ['OPEN PRICE (Rs.)', 'Year', 'Month', 'Day'] if col in df.columns]

    df = df.dropna(subset=['CLOSE PRICE (Rs.)'])
    if df.empty:
        return jsonify({"error": f"No valid data for {company_name}"}), 400

    X = df[features]
    y = df['CLOSE PRICE (Rs.)']
    X = X.fillna(X.mean())

    if len(X) < 2:
        return jsonify({"error": f"Not enough data for {company_name} to train the model"}), 400

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    model_path = os.path.join(RESULTS_FOLDER, f"{company_name}_model.pkl")
    dump(model, model_path)

    # Predictions
    y_pred = model.predict(X_test)

    df_test = X_test.copy()
    df_test['Actual CLOSE PRICE (Rs.)'] = y_test.values
    df_test['Predicted CLOSE PRICE (Rs.)'] = y_pred
    result_file = os.path.join(RESULTS_FOLDER, f'{company_name}_predictions.xlsx')
    df_test.to_excel(result_file, index=False)

    # Model Performance Metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    performance_data = {
        'Company': company_name,
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R² Score': r2,
        'Model Path': model_path
    }
    predictions_collection.insert_one(performance_data)

    # Insert Predictions into MongoDB
    predictions_data = []
    for actual, predicted, features_row in zip(y_test, y_pred, X_test.to_dict(orient="records")):
        predictions_data.append({
            'Company': company_name,
            'Actual_Close_Price': actual,
            'Predicted_Close_Price': predicted,
            'Features': features_row
        })

    if predictions_data:
        predictions_collection.insert_many(predictions_data)

    return jsonify({
        "message": f"Model trained and predictions saved for {company_name}",
        "performance": performance_data,
        "prediction_file": result_file
    })

from waitress import serve

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)