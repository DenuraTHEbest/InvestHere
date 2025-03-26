import os
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, confusion_matrix, classification_report
)
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# =======================================
# 1) Configuration
# =======================================
# Path to your CSV file containing stock data for 312 companies (2019-2024)
input_csv = r"BigPreprocess\big_one.csv"

# Output directory for predictions and model
output_directory = r"stock_predictions9"
os.makedirs(output_directory, exist_ok=True)

# --- Define Base and Optional Features ---
# Base features (these MUST exist in your file)
base_features = [
    'Year', 'Month', 'Day',
    'RSI_14',
    'MACD_Line', 'MACD_Signal', 'MACD_Hist',
    'BB_Mid', 'BB_Upper', 'BB_Lower',
    'Volume_Change',
    'ATR_14'
]
# Optional features: if your file already has lag features and moving averages, include them.
optional_features = [f'CLOSE PRICE (Lag {i})' for i in range(1, 31)] + ['MA_7', 'MA_14', 'MA_30']

# Combine them into the final required feature list.
required_features = base_features + [col for col in optional_features if col in pd.read_csv(input_csv, nrows=5).columns]

# =======================================
# 2) Load and Validate the Dataset
# =======================================
try:
    df = pd.read_csv(input_csv, decimal='.', engine='python')
except Exception as e:
    print(f"Error reading {input_csv}: {e}")
    raise SystemExit("❌ Could not read the input CSV. Exiting.")

# Ensure TRADING DATE exists
if 'TRADING DATE' not in df.columns:
    raise SystemExit("❌ 'TRADING DATE' column not found in the dataset. Exiting.")

# Convert TRADING DATE to datetime and create date features.
df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'], errors='coerce')
df = df.dropna(subset=['TRADING DATE'])
df['Year'] = df['TRADING DATE'].dt.year
df['Month'] = df['TRADING DATE'].dt.month
df['Day'] = df['TRADING DATE'].dt.day

# Check that the target column exists.
if 'OPEN PRICE (Rs.)' not in df.columns:
    raise SystemExit("❌ 'OPEN PRICE (Rs.)' (target) not found in the dataset. Exiting.")

# (Optional) Force numeric conversion on any required feature columns.
for col in required_features:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop rows where the target is missing.
df = df.dropna(subset=['OPEN PRICE (Rs.)'])
if df.empty:
    raise SystemExit("❌ No valid data left after dropping NaNs in target. Exiting.")

# =======================================
# 3) Prepare Features and Target
# =======================================
# Ensure all required features are present; if any are missing from df, print a warning.
missing_feats = [feat for feat in required_features if feat not in df.columns]
if missing_feats:
    print(f"⚠️ The following feature(s) are missing from the CSV and will not be used: {missing_feats}")
    required_features = [feat for feat in required_features if feat in df.columns]

# Drop rows with missing values in any required features.
df = df.dropna(subset=required_features)

# Set up feature matrix X and target vector y.
X = df[required_features].copy()
X = X.fillna(X.mean())
y = df["OPEN PRICE (Rs.)"]

if len(X) < 2:
    raise SystemExit("❌ Not enough data to train. Exiting.")

# =======================================
# 4) Train/Test Split
# =======================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.35, random_state=42
)

# =======================================
# 5) Define and Train the Model with Hyperparameter Tuning
# =======================================
param_grid = {
    'n_estimators': [50, 100, 150],
    'max_depth': [6, 8, 10],
    'min_samples_split': [5, 10, 15],
    'min_samples_leaf': [2, 5, 10]
}

rf = RandomForestRegressor(random_state=42)
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid,
                           cv=3, n_jobs=-1, scoring='r2', verbose=1)

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_

print("✅ Model trained successfully!")
print("Best parameters found:", grid_search.best_params_)

# =======================================
# 6) Iterative Forecast for 20 Days
# =======================================
n_days = 20
predictions = np.zeros((X_test.shape[0], n_days))
# Make a copy for iterative forecasting; technical indicator features remain static.
current_features = X_test.copy()

for day in range(n_days):
    # Predict using current features.
    day_predictions = best_model.predict(current_features)
    predictions[:, day] = day_predictions

    if day < n_days - 1:
        # If optional lag features are available, update them.
        lag_cols = [f'CLOSE PRICE (Lag {i})' for i in range(1, 31)]
        if all(col in current_features.columns for col in lag_cols):
            # Shift lag features: Lag 1 becomes Lag 2, ..., Lag 29 becomes Lag 30.
            for i in range(30, 1, -1):
                current_features[f'CLOSE PRICE (Lag {i})'] = current_features[f'CLOSE PRICE (Lag {i - 1})']
            # Update Lag 1 with today's prediction.
            current_features['CLOSE PRICE (Lag 1)'] = day_predictions

            # Recalculate moving averages if present.
            for ma_col, window in [('MA_7', 7), ('MA_14', 14), ('MA_30', 30)]:
                if ma_col in current_features.columns:
                    current_features[ma_col] = current_features[[f'CLOSE PRICE (Lag {i})' for i in range(1, window + 1)]].mean(axis=1)

        # Update date features for the next day.
        dates = pd.to_datetime(current_features[['Year', 'Month', 'Day']])
        dates += pd.Timedelta(days=1)
        current_features['Year'] = dates.dt.year
        current_features['Month'] = dates.dt.month
        current_features['Day'] = dates.dt.day

        # Fill any potential NaN values.
        current_features = current_features.fillna(current_features.mean())

# =======================================
# 7) Store Predictions & Evaluate
# =======================================
df_test = X_test.copy()
for i in range(1, n_days + 1):
    df_test[f"Predicted Day {i}"] = predictions[:, i - 1]

df_test["Actual Day 1"] = y_test.values
df_test = df_test.sort_values(by=['Year', 'Month', 'Day'])

csv_filename = "big_one_predictions_20days.csv"
local_file_path = os.path.join(output_directory, csv_filename)
df_test.to_csv(local_file_path, index=False)
print(f"📁 Saved 20-day predictions to '{local_file_path}'")

# =======================================
# 8) Compute Day 1 Regression Metrics
# =======================================
all_y_test = y_test.values
all_y_pred_day1 = predictions[:, 0]

assert len(all_y_pred_day1) == len(all_y_test), "Mismatch in number of samples between true and predicted values (Day 1)."

mae_day1 = mean_absolute_error(all_y_test, all_y_pred_day1)
mse_day1 = mean_squared_error(all_y_test, all_y_pred_day1)
r2_day1 = r2_score(all_y_test, all_y_pred_day1)

print("\n📊 Day 1 Regression Metrics:")
print(f"Mean Absolute Error (MAE): {mae_day1:.3f}")
print(f"Mean Squared Error (MSE): {mse_day1:.3f}")
print(f"R-squared (R2):            {r2_day1:.3f}")

# =======================================
# 9) Classification-Like Accuracy & Confusion Matrix
# =======================================
# For a classification-like view, we compare whether the predicted Day 1 OPEN PRICE is above the (optional) Lag 1 value.
if "CLOSE PRICE (Lag 1)" in X_test.columns:
    lag1_test = X_test["CLOSE PRICE (Lag 1)"].values
else:
    # If not available, use a zero array (or another reference) for classification.
    lag1_test = np.zeros(len(X_test))
actual_updown = (all_y_test > lag1_test).astype(int)
pred_updown = (all_y_pred_day1 > lag1_test).astype(int)

acc_score = accuracy_score(actual_updown, pred_updown)
print(f"\n📊 Day 1 Up/Down Classification Accuracy: {acc_score:.3f}")

cm = confusion_matrix(actual_updown, pred_updown)
print("Confusion Matrix:\n", cm)
print("Classification Report:\n", classification_report(actual_updown, pred_updown, digits=3))

plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=["Down (0)", "Up (1)"],
            yticklabels=["Down (0)", "Up (1)"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix (Day 1 Up/Down)")
plt.show()

# =======================================
# 10) Save the Trained Model
# =======================================
model_filename = os.path.join(output_directory, "20daysModel.pkl")
joblib.dump(best_model, model_filename)
print(f"✅ Trained RandomForestRegressor model saved to '{model_filename}'.")
