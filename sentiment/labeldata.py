# Import libraries
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import pandas as pd
import torch
from sklearn.model_selection import train_test_split

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("NLPC-UOM/SinBERT-large")
model = AutoModelForSequenceClassification.from_pretrained("NLPC-UOM/SinBERT-large", num_labels=3)

# Specify column names for labeled and unlabeled datasets
labeled_text_column = 'comment'
labeled_label_column = 'label'
unlabeled_text_column = 'Description'

# Load and preprocess labeled data
labeled_data = pd.read_csv("/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/LabellingData/data/sinhala_news_sentiment.csv")
print("Labeled Dataset Columns:", labeled_data.columns)

# Check if the specified columns exist
if labeled_text_column not in labeled_data.columns or labeled_label_column not in labeled_data.columns:
    raise KeyError(f"Make sure '{labeled_text_column}' and '{labeled_label_column}' exist in labeled dataset.")

# Encode labels for training
label_map = {label: idx for idx, label in enumerate(labeled_data[labeled_label_column].unique())}
labeled_data['encoded_label'] = labeled_data[labeled_label_column].map(label_map)

# Split labeled data for training and validation
train_data, val_data = train_test_split(labeled_data, test_size=0.2, random_state=42)

# Tokenization function
def tokenize_data(data, text_column):
    return tokenizer(
        list(data[text_column]),
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors='pt'
    )

# Tokenize labeled training and validation data
train_encodings = tokenize_data(train_data, labeled_text_column)
val_encodings = tokenize_data(val_data, labeled_text_column)

# Prepare PyTorch Dataset objects
class SentimentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = SentimentDataset(train_encodings, train_data['encoded_label'].tolist())
val_dataset = SentimentDataset(val_encodings, val_data['encoded_label'].tolist())

# Training arguments and setup
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# Train the model
trainer.train()

# Load and preprocess the unlabeled dataset
unlabeled_data = pd.read_csv("news_data.csv")
print("Unlabeled Dataset Columns:", unlabeled_data.columns)

# Check if the specified text column exists in unlabeled data
if unlabeled_text_column not in unlabeled_data.columns:
    raise KeyError(f"Make sure '{unlabeled_text_column}' exists in the unlabeled dataset.")

# Tokenize unlabeled data
unlabeled_encodings = tokenizer(
    list(unlabeled_data[unlabeled_text_column].astype(str)),
    truncation=True,
    padding=True,
    max_length=512,
    return_tensors='pt'
)

# Prepare a dataset compatible with Trainer for prediction
class UnlabeledSentimentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: val[idx] for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings['input_ids'])

unlabeled_dataset = UnlabeledSentimentDataset(unlabeled_encodings)

# Predict on unlabeled data
predictions = trainer.predict(unlabeled_dataset)

# Get predicted labels
predicted_labels = torch.argmax(torch.tensor(predictions.predictions), axis=1)

# Map predicted labels back to original labels (if applicable)
reverse_label_map = {v: k for k, v in label_map.items()}
unlabeled_data['predicted_label'] = [reverse_label_map[label.item()] for label in predicted_labels]

# Save the predictions to a new CSV
unlabeled_data.to_csv("/Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/LabellingData/data/predictions.csv", index=False)
print("Predictions saved to /Users/athukoralagekavishanvishwajith/Desktop/AIDS/Year2/DSGP/LabellingData/data/predictions.csv")
