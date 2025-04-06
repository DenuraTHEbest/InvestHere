from pymongo import MongoClient
import certifi
import joblib
import pandas as pd
import datetime

# MongoDB URI
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"

# Connect to MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['aspi_database']
collection = db['aspi_data']

print("✅ Connected to MongoDB Atlas successfully!")

# Load the trained model
model_path = "aspi_forecast_model_new.pkl"
model = joblib.load(model_path)
print("✅ Model loaded successfully!")

# Load the test target results (actual values)
target_path = "aspi_test_targets.csv"
target = pd.read_csv(target_path)

# Load the test dataset (features for predictions)
test_data_path = "aspi_test_features.csv"  # Update with your actual file path
test_data = pd.read_csv(test_data_path)

# Predict ASPI prices (ensure this is your correct input format)
predictions = model.predict(test_data)

# Convert predictions into a DataFrame
predictions_df = pd.DataFrame(predictions, columns=[f'Predicted_Day_{i}' for i in range(1, 21)])
predictions_df.insert(0, 'Date', test_data['Date'])  # Add Date column

# Convert the Date column from Unix timestamp to normal date
def convert_date(unix_time):
    return datetime.datetime.fromtimestamp(int(unix_time)).strftime('%Y-%m-%d')

# Assuming 'Date' is in Unix timestamp format
predictions_df['Date'] = predictions_df['Date'].apply(convert_date)

# Convert the 'Date' column to datetime objects
predictions_df['Date'] = pd.to_datetime(predictions_df['Date'], format='%Y-%m-%d')

target_values_for_predictions = target.iloc[-len(predictions_df):]  # Get last N rows, N = number of predictions

# Add target values (actuals) to the predictions dataframe
for i in range(1, 21):  # 20 days of predictions
    predictions_df[f'Actual_Day_{i}'] = target_values_for_predictions[f'Target_{i}'].values

# Convert predictions DataFrame into a dictionary format for MongoDB
predictions_dict = predictions_df.to_dict(orient="records")

# Get only the last row (if required)
last_prediction = predictions_dict[-1]  # This gets the last entry
predictions_dict = [last_prediction]  # You can modify this if you need all rows

print("✅ Predictions and targets converted to dictionary format!")

# Insert predictions into MongoDB
collection.insert_many(predictions_dict)

print("✅ Predictions and actuals inserted into MongoDB successfully!")

predictions_dict = predictions_df.to_dict(orient="records")

# adding the corresponding actual values to the predictions into the database
# Extract Date, Predicted_Day_1, and Actual_Day_1 for the required 20 rows
required_data = [{"Date": entry["Date"], "Predicted_Day_1": entry["Predicted_Day_1"], "Actual_Day_1": entry["Actual_Day_1"]} for entry in predictions_dict[-40:-20]]
predictions_dict = required_data

# Insert predictions into MongoDB
collection.insert_many(predictions_dict)

# Retrieve and print one document to verify
sample_prediction = collection.find_one()
print("Sample prediction from MongoDB:", sample_prediction)
