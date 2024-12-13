import os
import uuid
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from google.cloud.dialogflow_v2 import SessionsClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load the fine-tuned model and tokenizer
model = GPT2LMHeadModel.from_pretrained('./fine_tuned_gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('./fine_tuned_gpt2')

# Set the pad token to EOS token for consistency
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)  # Move the model to the appropriate device

# Define a simplified therapist prompt with examples for context
therapist_prompt = (
    "You are a compassionate AI therapist. Respond empathetically to user inquiries."
)

# Function to generate text with improved logic
def generate_text(user_input, max_length=100, temperature=0.7, top_k=30, top_p=0.8, repetition_penalty=1.5):
    try:
        # Reinforced prompt with examples
        prompt = (
            f"{therapist_prompt}\n"
            "User: What is the color of the sky?\n"
            "Sage: The sky is blue on a clear day.\n"
            "User: Why do people feel sad?\n"
            "Sage: It's natural to feel sad sometimes. Emotions help us process our experiences.\n"
            f"User: {user_input}\nSage:"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(device)
        attention_mask = inputs.attention_mask
        
        output = model.generate(
            inputs.input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=True,
            repetition_penalty=repetition_penalty,
            pad_token_id=tokenizer.pad_token_id
        )
        
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract and validate Sage's response
        if "Sage:" in response:
            response = response.split("Sage:")[-1].strip()
        
        # Basic validation to filter irrelevant responses
        if response.lower() in ["i don't know", "i'm not sure"]:
            response = "I'm here to help, but I might need more information to answer your question."
        
        return response
    except Exception as e:
        print(f"Error in text generation: {e}")
        return "I'm sorry, I couldn't process your input."

# Initialize Dialogflow API client
session_client = SessionsClient()

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('text')
    if not user_input or user_input.strip() == "":
        return jsonify({'response': "I'm sorry, I didn't understand that."}), 400

    try:
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        
        if not project_id:
            return jsonify({'response': "Google Cloud project ID is not set in environment."}), 500
        
        session_path = session_client.session_path(project_id, session_id)

        # Dialogflow request
        response = session_client.detect_intent(
            session=session_path,
            query_input={
                'text': {
                    'text': user_input,
                    'language_code': 'en-US'
                }
            }
        )

        bot_response = response.query_result.fulfillment_text
        
        print('Dialogflow response:', bot_response)

        # If Dialogflow does not provide a valid response or matches an unrecognized intent:
        if not bot_response or "I didn't get that" in bot_response:
            print("No recognized intent; generating response using Sage.")
            bot_response = generate_text(user_input)  # Use GPT-2 for generating a response

        return jsonify({'response': bot_response})

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'response': "I'm sorry, there was an error processing your request."}), 500

if __name__ == '__main__':
    app.run(port=5000)