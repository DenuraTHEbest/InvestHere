from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load pre-trained model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Put the model in evaluation mode
model.eval()

def generate_response(input_text):
    # Encode the input text into tokens
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Generate a response
    with torch.no_grad():
        output = model.generate(input_ids, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2, pad_token_id=tokenizer.eos_token_id)

    # Decode the generated response
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return response

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break
    response = generate_response(user_input)
    print("Chatbot:", response)