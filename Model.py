import pandas as pd
import os
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

input_directory = r'C:\Users\nimsi\OneDrive\Documents\DSGP_Datasets'
output_directory = r'C:\Users\nimsi\OneDrive\Documents\DSGP_Datasets\results'
os.makedirs(output_directory, exist_ok=True)

file_paths = glob(os.path.join(input_directory, '*.xlsx'))

results = []

for file_path in file_paths:
    company_name = os.path.splitext(os.path.basename(file_path))[0]
    df = pd.read_excel(file_path)

    if 'TRADING DATE' in df.columns:
        df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'])
        df['Year'] = df['TRADING DATE'].dt.year
        df['Month'] = df['TRADING DATE'].dt.month
        df['Day'] = df['TRADING DATE'].dt.day
    else:
        df['Year'], df['Month'], df['Day'] = [None] * 3

    features = [col for col in ['PRICE HIGH (Rs.)', 'PRICE LOW (Rs.)', 'OPEN PRICE (Rs.)',
                                'TRADE VOLUME (No.)', 'SHARE VOLUME (No.)', 'TURNOVER (Rs.)',
                                'Year', 'Month', 'Day'] if col in df.columns]

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
    df_test.to_excel(os.path.join(output_directory, f'{company_name}_predictions.xlsx'), index=False)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    results.append({'Company': company_name, 'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R² Score': r2})

results_df = pd.DataFrame(results)
results_df.to_excel(os.path.join(output_directory, 'overall_model_performance.xlsx'), index=False)

print("Model training, predictions, and accuracy evaluation completed for all companies.")
