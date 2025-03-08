from pymongo import MongoClient

# Replace with your actual connection string
MONGO_URI = "mongodb+srv://kavishanvishwajith:BjNG7kGpWeLUJXNc@cluster01.e5p2x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster01"
# Connect to MongoDB
import certifi
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())


# Access the database
db = client['aspi_database']

# Access the collection
collection = db['aspi_predictions']

print("Connected to MongoDB Atlas successfully!")

import joblib
import pandas as pd

# Load the trained model
# Load the model
model_path = "aspi_forecast_model_new.pkl"
model = joblib.load(model_path)

# Debugging: Check model type
print(f"Model type: {type(model)}")  # Should be a trained RandomForestRegressor or MultiOutputRegressor

print("✅ Model loaded successfully!")

# Load the test dataset
test_data_path = "aspi_test_features.csv"  # Update path
test_data = pd.read_csv(test_data_path)

# Predict ASPI prices
#predictions = model.predict(test_data.drop(columns=['Date']))  # Drop 'Date' before prediction
predictions = model.predict(test_data) 

# Convert predictions into a DataFrame
predictions_df = pd.DataFrame(predictions, columns=[f'Predicted_Day_{i}' for i in range(1, 21)])
predictions_df.insert(0, 'Date', test_data['Date'])  # Add Date column

# Convert predictions DataFrame into a dictionary format for MongoDB
predictions_dict = predictions_df.to_dict(orient="records")

#Getting only the last row of the predictions dictionary
last_prediction = predictions_dict[-1]
predictions_dict=[last_prediction]

print("✅ Predictions converted to dictionary format!")

print(type(predictions_dict))  # Should be <class 'list'>
print(len(predictions_dict))   # Should be greater than 0
print(predictions_dict[:2])    # Print the first two records for debugging

try:
    client.admin.command('ping')
    print("✅ MongoDB connection verified!")
except Exception as e:
    print("❌ Connection error:", e)

# Insert predictions into MongoDB
collection.insert_many(predictions_dict)

print("✅ Predictions inserted into MongoDB successfully!")

# Retrieve and print one document to verify
sample_prediction = collection.find_one()
print("Sample prediction from MongoDB:", sample_prediction)



    
