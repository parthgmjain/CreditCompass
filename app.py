from flask import Flask, render_template, request, jsonify
import requests  
import os
from dotenv import load_dotenv  

# ✅ Load environment variables
load_dotenv()
API_KEY = os.getenv("LETTA_API_KEY")
if not API_KEY:
    raise ValueError("❌ ERROR: LETTA_API_KEY is missing from .env file")

app = Flask(__name__)

# ✅ Letta AI Configuration
AGENT_ID = "agent-7a3b2942-3050-4751-b63e-670b927d02a0"
LETTA_API_URL = f"http://localhost:8283/v1/agents/{AGENT_ID}/messages"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/letta')
def letta():
    return render_template('letta.html')

@app.route('/questions')
def questions():
    return render_template('questions.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/generate_timeline', methods=['POST'])
def generate_timeline():
    """Fetch credit recommendations from Letta.ai"""
    user_data = request.json

    if "messages" not in user_data or not isinstance(user_data["messages"], list):
        return jsonify({"error": "Invalid request format. 'messages' array is required."}), 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        print("📡 Sending request to Letta AI...")
        print(f"🔹 Request Data: {user_data}")

        response = requests.post(LETTA_API_URL, json=user_data, headers=headers)

        print(f"📝 Response Status: {response.status_code}")
        
        # ✅ Check for API response errors
        if response.status_code != 200:
            print(f"❌ Error Response: {response.text}")
            return jsonify({
                "error": f"Failed to fetch recommendations, status: {response.status_code}",
                "details": response.text
            }), response.status_code

        # ✅ Parse response safely
        try:
            response_json = response.json()
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")
            return jsonify({"error": "Invalid JSON response from Letta AI."}), 500

        print(f"🔍 API Response Data: {response_json}")

        return jsonify(response_json)  # ✅ Return successful response

    except requests.exceptions.RequestException as e:
        print(f"🔥 API request failed: {e}")
        return jsonify({"error": f"API request failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
