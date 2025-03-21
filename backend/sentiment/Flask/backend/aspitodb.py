from datetime import datetime  # Corrected import
import pandas as pd
from pymongo import MongoClient
import certifi
import os

# MongoDB Atlas connection details
username = "kavishanvishwajith"
password = "BjNG7kGpWeLUJXNc"
cluster_url = "cluster01.e5p2x.mongodb.net"
database_name = "test"

# Construct the connection string
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_url}/{database_name}?retryWrites=true&w=majority"

# Connect to MongoDB Atlas with SSL
try:
    client = MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())
    db = client[database_name]
    daily_scores_collection = db["test"]  # Use the 'aspi' collection
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")
    exit()

# Read CSV file
file_path = "/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/InvestHERE/Untitled/sentiment/Data/Weighted_Scores/daily_weighted_score.csv"  # Update with the actual path

# Check if the CSV file exists
if not os.path.exists(file_path):
    print(f"❌ CSV file not found at: {file_path}")
    exit()

try:
    df = pd.read_csv(file_path)
    print("✅ CSV file read successfully!")
except Exception as e:
    print(f"❌ Failed to read CSV file: {e}")
    exit()

# Convert the DataFrame to a list of dictionaries
data = []
for index, row in df.iterrows():
    try:
        record = {
            "date": datetime.strptime(row['Date'], '%Y-%m-%d'),  # Ensure 'Date' column exists
            "negative": row['0'],
            "neutral": row['1'],
            "positive": row['2'],
            "total": row['Total'],
            "weighted_score": row['Weighted_Score']
        }
        data.append(record)
    except KeyError as e:
        print(f"❌ Missing column in CSV file: {e}")
        exit()
    except Exception as e:
        print(f"❌ Error processing row {index + 1}: {e}")
        exit()

# Insert the data into MongoDB
try:
    daily_scores_collection.insert_many(data)
    print("✅ Data inserted successfully!")
except Exception as e:
    print(f"❌ Failed to insert data into MongoDB: {e}")

'''# Clean and format the data
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['Price'] = df['Price'].str.replace(',', '').astype(float)
df['Open'] = df['Open'].str.replace(',', '').astype(float)
df['High'] = df['High'].str.replace(',', '').astype(float)
df['Low'] = df['Low'].str.replace(',', '').astype(float)

# Handle volume (convert 'M' to millions and 'B' to billions)
# Handle volume (convert 'M' to millions, 'B' to billions, 'K' to thousands)
def convert_volume(vol):
    if isinstance(vol, str):
        if 'M' in vol:
            return float(vol.replace('M', '')) * 1_000_000
        elif 'B' in vol:
            return float(vol.replace('B', '')) * 1_000_000_000
        elif 'K' in vol:
            return float(vol.replace('K', '')) * 1_000
        elif vol == '-':
            return None
    try:
        return float(vol) if vol else None
    except ValueError:
        return None

df['Vol.'] = df['Vol.'].apply(convert_volume)

# Convert change percentage to float
df['Change %'] = df['Change %'].str.replace('%', '').astype(float) / 100

# Insert data into MongoDB
for _, row in df.iterrows():
    record = {
        'date': row['Date'].strftime('%Y-%m-%d'),
        'price': row['Price'],
        'open': row['Open'],
        'high': row['High'],
        'low': row['Low'],
        'volume': row['Vol.'],  # Volume in raw units
        'change_percent': row['Change %']
    }
    
    # Upsert data based on the date
    aspi_collection.update_one(
        {'date': record['date']},
        {'$set': record},
        upsert=True
    )

print("✅ ASPIs inserted/updated successfully!")'''