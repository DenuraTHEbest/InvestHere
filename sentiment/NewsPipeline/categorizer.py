from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load category model
tokenizer = AutoTokenizer.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")
model = AutoModelForSequenceClassification.from_pretrained("sinhala-nlp/NSINA-Category-sinbert-large")

category_labels = {0: "business news", 1: "international news", 2: "local news", 3: "sports news"}

def categorize_news(title):
    inputs = tokenizer([title], return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    category = category_labels.get(torch.argmax(outputs.logits, dim=1).item(), "unknown")
    return category