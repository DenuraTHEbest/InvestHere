import pandas as pd
import joblib
import requests

# Load the pre-trained model (already saved after training)
model = joblib.load('aspi_forecast_model_new.pkl')

# Load the new test data from the CSV file
new_test_data = pd.read_csv("aspi_test_features.csv")

# Predict using the pre-trained model
y_pred = model.predict(new_test_data)

# get the last row of the predictions
y_pred = y_pred[-1]  # Get the last row of predictions

# Print the predictions
print("Predictions for the new test data:")
print(y_pred)

import sys
decimal_value = float(sys.argv[1])  # Gets the decimalValue from Flask

actual_value = decimal_value  # Replace with the actual value for the earliest day without an actual value

# Step 1: Fetch the last 20 days of data from the database
response = requests.get("http://localhost:5050/")  # Fetch data from the backend
if response.status_code == 200:
    data = response.json()
    last_20_days = data[-20:]  # Get the last 20 days of data
else:
    print("Error fetching data from the database:", response.json())
    exit()

# Step 2: Add predictions to the last 20 days of data
for i, row in enumerate(last_20_days):
    if i < len(y_pred):
        row["predicted"] = float(y_pred[-(i + 1)])  # Reverse the mapping of predictions
# Step 3: Update the actual value for the earliest day without an actual value
for row in last_20_days:
    if row["actual"] is None:  # Find the first day without an actual value
        row["actual"] = actual_value  # Update it with the defined actual value
        break  # Stop after updating the first such day

# Step 4: Send the updated data back to the database
update_response = requests.post("http://localhost:5050/update-predictions", json=last_20_days)
if update_response.status_code == 200:
    print("Predictions updated successfully in the database.")
else:
    print("Error updating predictions in the database:", update_response.json())