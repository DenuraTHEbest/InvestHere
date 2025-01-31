import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm  # Import tqdm for progress bar

# Load the dataset
file_path = "news_data.csv"  # Replace with your file path
df = pd.read_csv(file_path)

# Load SinBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("NLPC-UOM/SinBERT-large")
model = AutoModelForSequenceClassification.from_pretrained("NLPC-UOM/SinBERT-large")

## Define a function to predict sentiment
def predict_sentiment(text):
    if pd.isnull(text):  # Handle missing or NaN values
        return "neutral"  # Assign a default label, or handle as needed

    # Tokenize text with truncation and padding
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512  # Ensure inputs fit within model limits
    )

    # Pass through the model
    outputs = model(**inputs)

    # Get sentiment label from logits
    predicted_label = torch.argmax(outputs.logits, dim=1).item()

    # Map numerical labels to sentiments
    sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
    return sentiment_map[predicted_label]

# Add progress tracking for sentiment labeling
progress = []  # Store results temporarily

for index, description in tqdm(df["Description"].items(), total=len(df), desc="Processing Sentiments"):
    sentiment = predict_sentiment(description)  # Predict sentiment for each row
    progress.append(sentiment)

# Add the sentiments to the DataFrame
df["predicted_sentiment"] = progress


# Save the updated dataset
output_file_path = "labeled_news_dataset.csv"
df.to_csv(output_file_path, index=False)

print("Sentiment labeling completed. Labeled dataset saved to", output_file_path)
