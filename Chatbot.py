from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load pre-trained model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Set pad_token to eos_token (End of Sequence)
tokenizer.pad_token = tokenizer.eos_token

# Put the model in evaluation mode
model.eval()

# Define stock market-related knowledge (to help the model with relevant terms)
stock_market_knowledge = {
    "stock": "A stock represents ownership in a company and constitutes a claim on part of the company’s assets and earnings.",
    "stock market": "The stock market is a collection of markets where stocks (equity securities), bonds, and other securities are bought and sold.",
    "technical indicators": "Technical indicators are statistical measures that traders use to evaluate and predict future price movements in a stock market.",
    "bull market": "A bull market is when the market is on the rise, with increasing stock prices.",
    "bear market": "A bear market is when the market is declining, and stock prices are falling.",
    "sentiment analysis": "Sentiment analysis involves using natural language processing to determine the emotional tone of news or social media to predict market movements.",
}

# Function to generate a response
def generate_response(input_text):
    # Check if the input contains any stock market terms for direct response
    for term, definition in stock_market_knowledge.items():
        if term in input_text.lower():
            return definition

    # Encode the input text into tokens, including attention mask
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    
    # Explicitly create an attention mask to avoid the warning
    attention_mask = inputs['attention_mask']

    # Generate a dynamic response for general conversation
    with torch.no_grad():
        output = model.generate(
            inputs['input_ids'],
            attention_mask=attention_mask,
            max_length=50,  # Limit the response length to avoid unnecessary output
            temperature=0.7,
            top_p=0.9,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True
        )

    # Decode the generated response and clean it up
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # Optional: Filter out the repeated prompt part (to avoid repetitive output)
    if input_text.lower() in response.lower():
        response = response.split(input_text, 1)[-1].strip()

    # If the response seems irrelevant (e.g., gibberish), pick a fallback message
    if "i don't know" in response.lower() or len(response.split()) < 3:
        response = "Sorry, I didn't quite catch that. Could you ask me something else?"

    return response.strip()

# Main loop for user interaction
print("Chatbot: Hello! I am your stock market assistant. Type 'exit' to end the conversation.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break
    
    response = generate_response(user_input)
    print("Chatbot:", response)
