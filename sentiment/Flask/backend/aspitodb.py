import pandas as pd
from pymongo import MongoClient
import certifi

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
    aspi_collection = db["aspi"]  # Use the 'aspi' collection
    print("✅ Connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")

# Read CSV file
file_path = "/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/InvestHERE/Untitled/sentiment/Data/ASPI_Data/CSE_All-Share_Historical_Data_(2).csv"  # Update with the actual path
df = pd.read_csv(file_path)

# Clean and format the data
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

print("✅ ASPIs inserted/updated successfully!")
