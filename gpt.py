from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)
CORS(app)

# Load pre-trained GPT-2 model and tokenizer
model_name = 'distilgpt2'  # You can use 'gpt2' for the full GPT-2 model
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

@app.route('/api/gpt2', methods=['POST'])
def gpt2_response():
    user_input = request.json.get('text')
    if not user_input or user_input.strip() == "":
        return jsonify({'response': "Please provide some input text."}), 400

    try:
        response = generate_gpt_response(user_input)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error generating GPT-2 response: {e}")
        return jsonify({'response': "Error generating response."}), 500

def generate_gpt_response(prompt):
    """Generate a response using the GPT-2 model."""
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(
        inputs,
        max_length=50,  # Adjust as needed
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        top_k=50,
        top_p=0.95,
        temperature=0.7
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()

if __name__ == '__main__':
    app.run(port=5000)  # Runs the server on port 5000
