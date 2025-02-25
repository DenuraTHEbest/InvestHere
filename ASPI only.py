import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_validate, TimeSeriesSplit
from datetime import datetime, timedelta

# Set base directory
base_dir = r"C:\\DSGP\\Latesttt\\data\\raw\\cleaned"

# Load all datasets
file_names = [
    "aspi_data1.csv", "gdp_data1.csv"
    #, "gdp_data1.csv", "gold_data1.csv", "inflation_data1.csv", "interestRate1.csv", "oil_data1.csv", "S&P20_data1.csv", "USD_LKR Historical Data1.csv"
]

datasets = {}

for file in file_names:
    file_path = os.path.join(base_dir, file)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        # df = df.dropna(subset=['Date'])  # Remove invalid dates
        datasets[file] = df
    else:
        print(f"Warning: {file} not found")

for name, df in datasets.items():
    print(f"{name}: {df.shape}")  # Should have rows > 0
    print(df.head())  # See if data exists

for file in file_names:
    file_path = os.path.join(base_dir, file)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Standardize format
        df = df.dropna(subset=['Date'])  # Remove invalid dates
        datasets[file] = df
    else:
        print(f"Warning: {file} not found")

merged_data = datasets["aspi_data1.csv"]
for name, df in datasets.items():
    if name != "aspi_data1.csv":
        merged_data = pd.merge(merged_data, df, on='Date', how='outer')  # Use 'outer' join

print("Shape after merging:", merged_data.shape)
print("Non-null rows:", merged_data.dropna().shape[0])  # Count valid rows

merged_data = merged_data.sort_values(by='Date')  # Ensure dates are in order
merged_data.fillna(method='ffill', inplace=True)  # Forward-fill missing values
merged_data.dropna(inplace=True)  # Drop any remaining NaNs if necessary

print(f"Merged Data Shape: {merged_data.shape}")
print(merged_data.head())

# Merge datasets on 'Date' column
merged_data = datasets["aspi_data1.csv"]
for name, df in datasets.items():
    if name != "aspi_data1.csv":
        merged_data = pd.merge(merged_data, df, on='Date', how='left')

# Sort data by Date
merged_data = merged_data.sort_values(by='Date')

# Define Target Variable (Predicting next day's ASPI price)
merged_data['Target'] = merged_data['Close'].shift(-1)
merged_data = merged_data.dropna()

# Features (Exclude Date & Target)
X = merged_data.drop(columns=['Date', 'Close'])
y = merged_data['Close']

## Define time series cross-validation strategy
cv = TimeSeriesSplit(n_splits=5)

# Train Initial Random Forest Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
cv_results = cross_validate(
    model, X, y, cv=cv,
    scoring=['neg_mean_squared_error', 'r2'],
    return_train_score=False
)

# Compute Performance Metrics
rmse_scores = np.sqrt(-cv_results['test_neg_mean_squared_error'])
r2_scores = cv_results['test_r2']
print(f"Mean RMSE: {rmse_scores.mean():.4f}")
print(f"Mean R2 Score: {r2_scores.mean():.4f}")

# Train Model on Full Data & Get Feature Importance
model.fit(X, y)
feature_importance = pd.Series(model.feature_importances_, index=X.columns)
feature_importance = feature_importance.sort_values(ascending=False)

# Plot Feature Importance
plt.figure(figsize=(10, 6))
feature_importance[:10].plot(kind='bar')
plt.title("Top 10 Feature Importances")
plt.show()

# Select Top Features & Retrain Model
selected_features = feature_importance[:5].index.tolist()
X_selected = merged_data[selected_features]
cv_results_selected = cross_validate(
    model, X_selected, y, cv=cv,
    scoring=['neg_mean_squared_error', 'r2'],
    return_train_score=False
)

# Compute Metrics for Selected Features Model
rmse_selected = np.sqrt(-cv_results_selected['test_neg_mean_squared_error'])
r2_selected = cv_results_selected['test_r2']
print(f"Refined Model - Mean RMSE: {rmse_selected.mean():.4f}")
print(f"Refined Model - Mean R2 Score: {r2_selected.mean():.4f}")
