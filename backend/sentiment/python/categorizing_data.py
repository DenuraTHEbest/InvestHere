from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")
model = AutoModelForSequenceClassification.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")

# Define category labels based on the model’s expected output
category_labels = {0: "business news", 1: "international news", 2: "local news", 3: "sports news"}

# Load your dataset
data = pd.read_csv("data/time_dropped_simplifiedlabel_added.csv")

# Ensure all descriptions/title are strings
data['Title'] = data['Title'].fillna('').astype(str)

# Batch processing setup
batch_size = 32  # Adjust batch size based on your system's memory
predicted_categories = []

# Process each batch
for i in range(0, len(data), batch_size):
    batch_texts = data['Title'][i:i + batch_size].tolist()  # Get batch of descriptions
    inputs = tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    batch_predictions = torch.argmax(logits, dim=1).tolist()

    # Map predicted labels to category names
    batch_categories = [category_labels.get(pred, "unknown") for pred in batch_predictions]
    predicted_categories.extend(batch_categories)

    # Print progress
    print(f"Processed {min(i + batch_size, len(data))}/{len(data)} records")

# Add predictions to the DataFrame
data['predicted_category'] = predicted_categories

# Filter for business news
business_news = data[data['predicted_category'] == "business news"]

# Save the filtered data
business_news.to_csv("filtered_business_news_from_title.csv", index=False)

print("Filtered data saved as 'filtered_business_news.csv'")
