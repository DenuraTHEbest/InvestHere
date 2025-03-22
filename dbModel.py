import os
import numpy as np
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, confusion_matrix, classification_report
)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# =======================================
# 1) Configuration
# =======================================
# Path to your single big CSV file
input_csv = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\BigPreprocess\big_one.csv"

# Output directory
output_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\stock_predictions9"
os.makedirs(output_directory, exist_ok=True)  # Ensure the directory exists

# We assume you want to predict OPEN PRICE (Rs.), so we do NOT include it in the features below.
# We'll rely on the lagged prices and other numeric features to help predict the next open price.
required_features = [
    'Year', 'Month', 'Day'
] + [f'CLOSE PRICE (Lag {i})' for i in range(1, 11)] + ['MA_7', 'MA_14', 'MA_30']

# =======================================
# 2) Load and Validate the Dataset
# =======================================
try:
    df = pd.read_csv(input_csv, decimal='.', engine='python')
except Exception as e:
    print(f"Error reading {input_csv}: {e}")
    raise SystemExit("❌ Could not read the input CSV. Exiting.")

# Force numeric conversion where necessary
numeric_cols = ['OPEN PRICE (Rs.)'] + [f'CLOSE PRICE (Lag {i})' for i in range(1, 11)] + ['MA_7', 'MA_14', 'MA_30']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Check if TRADING DATE exists
if 'TRADING DATE' not in df.columns:
    raise SystemExit("❌ 'TRADING DATE' column not found in the dataset. Exiting.")

df['TRADING DATE'] = pd.to_datetime(df['TRADING DATE'], errors='coerce')
df = df.dropna(subset=['TRADING DATE'])  # Drop rows with invalid TRADING DATE

df['Year'] = df['TRADING DATE'].dt.year
df['Month'] = df['TRADING DATE'].dt.month
df['Day'] = df['TRADING DATE'].dt.day

# Ensure all required features exist
missing_feats = [feat for feat in required_features if feat not in df.columns]
if missing_feats:
    raise SystemExit(f"❌ Missing features {missing_feats} in the dataset. Exiting.")

# Check the target column
if 'OPEN PRICE (Rs.)' not in df.columns:
    raise SystemExit("❌ 'OPEN PRICE (Rs.)' not found in the dataset. Exiting.")

# Drop rows where the main target is NaN
df = df.dropna(subset=['OPEN PRICE (Rs.)'])
if df.empty:
    raise SystemExit("❌ No valid data left after dropping NaNs in target. Exiting.")

# =======================================
# 3) Prepare Features and Target
# =======================================
X = df[required_features].copy()
X = X.fillna(X.mean())  # Fill any missing numeric data
y = df['OPEN PRICE (Rs.)']

if len(X) < 2:
    raise SystemExit("❌ Not enough data to train. Exiting.")

# =======================================
# 4) Train/Test Split
# =======================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.35, random_state=42
)

# =======================================
# 5) Define and Train the Model
# =======================================
model = RandomForestRegressor(
    n_estimators=30,
    max_depth=6,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42
)

model.fit(X_train, y_train)
print("✅ Model trained successfully!")

# =======================================
# 6) Iterative Forecast for 20 Days
# =======================================
n_days = 20
predictions = np.zeros((X_test.shape[0], n_days))
current_features = X_test.copy()

for day in range(n_days):
    # Predict using current features
    predictions[:, day] = model.predict(current_features)

    if day < n_days - 1:
        # Shift Lag 1 to Lag 2, etc.
        for i in range(10, 1, -1):
            current_features[f'CLOSE PRICE (Lag {i})'] = current_features[f'CLOSE PRICE (Lag {i - 1})']

        # Use today's prediction as tomorrow's Lag 1
        current_features['CLOSE PRICE (Lag 1)'] = predictions[:, day]

        # Fill any potential NaN values
        current_features = current_features.fillna(current_features.mean())

# =======================================
# 7) Store Predictions & Evaluate
# =======================================
df_test = X_test.copy()

# Store Day-By-Day Predictions
for i in range(1, n_days + 1):
    df_test[f"Predicted Day {i}"] = predictions[:, i - 1]

# Also store the Actual Day 1 (the real y_test) for reference
df_test["Actual Day 1"] = y_test.values

# Sort for clarity
df_test = df_test.sort_values(by=['Year', 'Month', 'Day'])

# Save the day-by-day predictions
csv_filename = "big_one_predictions_20days.csv"
local_file_path = os.path.join(output_directory, csv_filename)
df_test.to_csv(local_file_path, index=False)
print(f"📁 Saved 20-day predictions to '{local_file_path}'")

# =======================================
# 8) Compute Day 1 Metrics (Regression)
# =======================================
all_y_test = y_test.values
all_y_pred_day1 = predictions[:, 0]  # The first day predictions

assert len(all_y_pred_day1) == len(all_y_test), \
    "Mismatch in number of samples between true and predicted values (Day 1)."

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
# We'll define "Up" if Day 1 is predicted higher than the test row's "CLOSE PRICE (Lag 1)."
# We'll define "Up" for actual if the actual Day 1 price is higher than "CLOSE PRICE (Lag 1)."
# This is a pseudo-classification approach.

import matplotlib.pyplot as plt
import seaborn as sns

lag1_test = X_test["CLOSE PRICE (Lag 1)"].values

# Actual Up/Down
actual_updown = (all_y_test > lag1_test).astype(int)  # 1 if actual open > lag1
pred_updown = (all_y_pred_day1 > lag1_test).astype(int)

# Accuracy
acc_score = accuracy_score(actual_updown, pred_updown)
print(f"\n📊 Day 1 Up/Down Classification Accuracy: {acc_score:.3f}")

# Confusion Matrix
cm = confusion_matrix(actual_updown, pred_updown)
print("Confusion Matrix:\n", cm)

# Classification Report
print("Classification Report:\n", classification_report(actual_updown, pred_updown, digits=3))

# Plot Graphical Confusion Matrix
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
model_filename = "20daysModel.pkl"
joblib.dump(model, model_filename)
print(f"✅ Trained RandomForestRegressor model saved to '{model_filename}'.")
