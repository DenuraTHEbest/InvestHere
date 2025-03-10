import pandas as pd
import os
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
from pymongo import MongoClient
import certifi
import gridfs
from io import BytesIO

# MongoDB Connection Setup
username = "kavishanvishwajith"
password = "BjNG7kGpWeLUJXNc"
cluster_url = "cluster01.e5p2x.mongodb.net"
database_name = "test"

mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority"

try:
    client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
    db = client[database_name]
    news_collection = db["news"]
    predictions_collection = db["predictions"]
    fs = gridfs.GridFS(db)  # GridFS for file storage
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")
    exit()

# Data Processing & Model Training
input_directory = r'C:\Users\nimsi\OneDrive\Documents\DSGP_Datasets'
output_directory = r'C:\Users\nimsi\OneDrive\Documents\DSGP_Datasets\stock_predictions'
os.makedirs(output_directory, exist_ok=True)  # Ensure the directory exists

file_paths = glob(os.path.join(input_directory, '*.xlsx'))

for file_path in file_paths:
    company_name = os.path.splitext(os.path.basename(file_path))[0]
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        continue

    if 'TRADING DATE' in df.columns:
        df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'])
        df['Year'] = df['TRADING DATE'].dt.year
        df['Month'] = df['TRADING DATE'].dt.month
        df['Day'] = df['TRADING DATE'].dt.day
    else:
        print(f"Warning: 'TRADING DATE' column not found in {company_name}. Skipping this file.")
        continue

    features = ['OPEN PRICE (Rs.)', 'Year', 'Month', 'Day']
    missing_features = [feature for feature in features if feature not in df.columns]
    if missing_features:
        print(f"Warning: Missing features {missing_features} in {company_name}. Skipping this file.")
        continue

    df = df.dropna(subset=['CLOSE PRICE (Rs.)'])
    if df.empty:
        print(f"Warning: No valid data for {company_name}. Skipping this file.")
        continue

    X = df[features]
    y = df['CLOSE PRICE (Rs.)']
    X = X.fillna(X.mean())

    if len(X) < 2:
        print(f"Warning: Not enough data for {company_name} to train the model. Skipping this file.")
        continue

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    df_test = X_test.copy()
    df_test['Actual CLOSE PRICE (Rs.)'] = y_test.values
    df_test['Predicted CLOSE PRICE (Rs.)'] = y_pred
    df_test = df_test.sort_values(by=['Year', 'Month', 'Day'])

    # Save DataFrame to an in-memory Excel file
    excel_buffer = BytesIO()
    df_test.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    # Store file in MongoDB using GridFS
    file_id = fs.put(excel_buffer, filename=f"{company_name}_predictions.xlsx")
    print(f"✅ Stored {company_name}_predictions.xlsx in MongoDB (File ID: {file_id})")

    # Save locally in 'stock_predictions' directory
    local_file_path = os.path.join(output_directory, f"{company_name}_predictions.xlsx")
    df_test.to_excel(local_file_path, index=False, engine='openpyxl')
    print(f"📁 Saved {company_name}_predictions.xlsx locally at {local_file_path}")

print("✅ Model training and file storage completed successfully.")