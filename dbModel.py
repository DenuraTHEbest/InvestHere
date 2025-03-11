import os
import pandas as pd
from glob import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

from retreive import fs

# Data Processing & Model Training
input_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\preprocessed2"
output_directory = r"C:\Users\nimsi\OneDrive\Documents\New_age_ML\stock_predictions4"
os.makedirs(output_directory, exist_ok=True)  # Ensure the directory exists

file_paths = glob(os.path.join(input_directory, '*.xlsx'))

# Lists to store all predictions and true labels for overall evaluation
all_y_test = []
all_y_pred = []

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

    features = ['OPEN PRICE (Rs.)', 'Year', 'Month', 'Day', 'CLOSE PRICE (Lag 1)', 'CLOSE PRICE (Lag 2)', 'CLOSE PRICE (Lag 3)', 'MA_7','MA_14','MA_30']
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

    # Store predictions and true labels for overall evaluation
    all_y_test.extend(y_test.values)
    all_y_pred.extend(y_pred)

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

# Convert predictions and true labels to numpy arrays for overall evaluation
all_y_test = pd.Series(all_y_test)
all_y_pred = pd.Series(all_y_pred)

# Regression Metrics for Overall Model
mae = mean_absolute_error(all_y_test, all_y_pred)
mse = mean_squared_error(all_y_test, all_y_pred)
r2 = r2_score(all_y_test, all_y_pred)

print("\n📊 Overall Regression Metrics:")
print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"R-squared (R2): {r2}")

# Classification Metrics for Overall Model (Optional: Convert to Classification Problem)
# Example: Predict if the price will go up (1) or down (0)
all_y_test_class = (all_y_test > all_y_test.shift(1)).astype(int)
all_y_pred_class = (all_y_pred > all_y_test.shift(1)).astype(int)

accuracy = accuracy_score(all_y_test_class, all_y_pred_class)
f1 = f1_score(all_y_test_class, all_y_pred_class)
precision = precision_score(all_y_test_class, all_y_pred_class)
recall = recall_score(all_y_test_class, all_y_pred_class)
conf_matrix = confusion_matrix(all_y_test_class, all_y_pred_class)

print("\n📊 Overall Classification Metrics:")
print(f"Accuracy: {accuracy}")
print(f"F1-Score: {f1}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"Confusion Matrix:\n{conf_matrix}")

# Plot Graphical Confusion Matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Predicted Down (0)', 'Predicted Up (1)'],
            yticklabels=['Actual Down (0)', 'Actual Up (1)'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

print("✅ Model training, evaluation, and file storage completed successfully.")