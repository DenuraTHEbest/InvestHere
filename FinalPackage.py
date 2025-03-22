import os
import pandas as pd
import numpy as np
from glob import glob
from datetime import datetime
from pymongo import MongoClient
import certifi
import joblib

# ----------------------------------------------------------------
# 1) MongoDB Configuration
# ----------------------------------------------------------------
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["IndividualDB2"]
collection = db["Compnay_Predictions2"]
print("✅ Connected to MongoDB Atlas successfully!")

# ----------------------------------------------------------------
# 2) Local Directories & Model Path
# ----------------------------------------------------------------
features_dir = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\preprocessed3"   # Directory with feature CSV files
actuals_dir  = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\ActualCSVfiles1"  # Directory with actual 20-day CSV files
model_path   = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\20daysModel.pkl"    # Path to the trained model file

# Load the trained model
model = joblib.load(model_path)
print("✅ Model loaded successfully!")

# ----------------------------------------------------------------
# 3) Define required features (must match the training features)
# ----------------------------------------------------------------
required_features = [
    'OPEN PRICE (Rs.)', 'Year', 'Month', 'Day',
    'CLOSE PRICE (Lag 1)', 'CLOSE PRICE (Lag 2)', 'CLOSE PRICE (Lag 3)',
    'MA_7', 'MA_14', 'MA_30'
]

# ----------------------------------------------------------------
# 4) Processing Loop over feature files
# ----------------------------------------------------------------
feature_files = glob(os.path.join(features_dir, "*.csv"))

for feat_file in feature_files:
    # Get the filename (e.g. "ACL_data.csv")
    company_filename = os.path.basename(feat_file)
    # Construct the expected actuals path (we assume the same filename)
    expected_actuals_path = os.path.join(actuals_dir, company_filename)

    # Load the features data
    try:
        df_features = pd.read_csv(feat_file)
    except Exception as e:
        print(f"❌ Could not read features for {company_filename}: {e}")
        continue

    # Determine the date information for merging.
    if "Date" in df_features.columns:
        try:
            df_features["Date"] = pd.to_datetime(df_features["Date"], errors='coerce')
            df_features["Year"] = df_features["Date"].dt.year
            df_features["Month"] = df_features["Date"].dt.month
            df_features["Day"] = df_features["Date"].dt.day
            df_features["Date"] = df_features["Date"].dt.strftime('%d-%m-%Y')
            merge_date = df_features["Date"].copy()
        except Exception as e:
            print(f"❌ Date conversion failed in features for {company_filename}: {e}")
            continue
        merge_date = df_features["Date"].copy()
    elif "TRADING DATE" in df_features.columns:
        try:
            df_features["TRADING DATE"] = pd.to_datetime(df_features["TRADING DATE"], errors='coerce')
            df_features['Year'] = df_features['TRADING DATE'].dt.year
            df_features['Month'] = df_features['TRADING DATE'].dt.month
            df_features['Day'] = df_features['TRADING DATE'].dt.day
            df_features["Date"] = df_features["TRADING DATE"].dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"❌ Date conversion failed in features for {company_filename}: {e}")
            continue
        merge_date = df_features["Date"].copy()
    else:
        merge_date = df_features.index.astype(str)

    # Verify that all required features exist.
    missing_feats = set(required_features) - set(df_features.columns)
    if missing_feats:
        print(f"⚠️ Missing required features {missing_feats} in {company_filename}. Skipping.")
        continue

    # Select only the required features.
    df_model_features = df_features[required_features].copy()

    # ----------------------------------------------------------------
    # (b) Run a 20-day rolling prediction FROM THE LAST ROW ONLY
    # ----------------------------------------------------------------
    n_days = 20
    last_row = df_model_features.iloc[[-1]].copy()  # Single row DataFrame for prediction
    X_iter = last_row.copy()
    predictions = np.zeros((1, n_days))

    for day in range(n_days):
        try:
            if day == 0:
                pred = model.predict(X_iter)  # expecting shape (1,)
                predictions[0, day] = pred[0]
            else:
                X_iter = X_iter.copy()
                X_iter['CLOSE PRICE (Lag 1)'] = predictions[0, day - 1]
                pred = model.predict(X_iter)
                predictions[0, day] = pred[0]
        except Exception as e:
            print(f"❌ Prediction failed on day {day+1} for {company_filename}: {e}")
            break

    pred_columns = [f"Predicted_Day_{i}" for i in range(1, n_days + 1)]
    final_date = merge_date.iloc[-1]
    df_preds = pd.DataFrame(predictions, columns=pred_columns)
    df_preds.insert(0, "Date", final_date)
    df_preds.insert(0, "Company_Name", company_filename)
    actual_final_value = last_row['OPEN PRICE (Rs.)'].iloc[0]
    df_preds.insert(2, "Actual_Final", actual_final_value)

    # ----------------------------------------------------------------
    # (c) Load actuals data and merge with predictions
    # ----------------------------------------------------------------
    if os.path.exists(expected_actuals_path):
        try:
            df_actuals = pd.read_csv(expected_actuals_path)
        except Exception as e:
            print(f"❌ Could not read actuals for {company_filename}: {e}")
            # Create dummy actuals using last day of features
            df_actuals = None
    else:
        print(f"⚠️ No actuals file found for {company_filename}. Using last day data from features as dummy actuals.")
        df_actuals = None

    if df_actuals is None:
        # Create a dummy dataframe with a single row using final_date and NaN for each Actual_Day_i.
        dummy_dict = {"Date": [final_date]}
        for i in range(1, n_days + 1):
            dummy_dict[f"Actual_Day_{i}"] = [np.nan]
        df_actuals = pd.DataFrame(dummy_dict)
    else:
        # Clean column names and process actuals as before.
        df_actuals.columns = df_actuals.columns.str.strip()
        rename_map = {f"Target_{i}": f"Actual_Day_{i}" for i in range(1, n_days + 1)}
        df_actuals.rename(columns=rename_map, inplace=True)
        if "Date" not in df_actuals.columns:
            try:
                df_actuals["Date"] = pd.to_datetime(df_actuals.index, errors='coerce').dt.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"❌ Could not create Date column in actuals for {company_filename}: {e}")
                continue
        else:
            try:
                df_actuals["Date"] = pd.to_datetime(df_actuals["Date"], errors='coerce').dt.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"❌ Date conversion failed in actuals for {company_filename}: {e}")
                continue

    try:
        df_final = pd.merge(df_preds, df_actuals, how="left", on="Date")
    except Exception as e:
        print(f"❌ Merge failed for {company_filename}: {e}")
        continue

    # ----------------------------------------------------------------
    # (d) Insert merged records into MongoDB
    # ----------------------------------------------------------------
    records_to_insert = df_final.to_dict(orient="records")
    if records_to_insert:
        try:
            collection.insert_many(records_to_insert)
            print(f"✅ Inserted {len(records_to_insert)} records for {company_filename} into MongoDB.")
        except Exception as e:
            print(f"❌ MongoDB insertion failed for {company_filename}: {e}")
    else:
        print(f"⚠️ Nothing to insert for {company_filename}.")

    sample_doc = collection.find_one({"Date": df_final["Date"].iloc[-1]})
    print("Sample doc from DB:", sample_doc)

print("\nAll done!")
