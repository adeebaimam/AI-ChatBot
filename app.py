import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Select the model
model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Generate response from Gemini AI
    response = model.generate_content(user_message)
    
    # Extract response text
    bot_reply = response.text if hasattr(response, "text") else "Error generating response."

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
