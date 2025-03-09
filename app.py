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
AGENT_ID = "agent-cb4f7fe1-a1e2-4db7-8410-227ad8180e6f"
LETTA_API_URL = f"https://api.letta.com/v1/agents/{AGENT_ID}/messages"

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
    """Fetch multiple credit card recommendations from Letta AI"""
    user_data = request.json
    print("🟢 Received request to /generate_timeline")
    print("🔍 Request Data:", user_data)  

    if not user_data or "messages" not in user_data:
        print("❌ Error: 'messages' key missing in request")
        return jsonify({"error": "Invalid request. 'messages' array is required."}), 400

    user_message = user_data["messages"][0]["content"]
    print(f"📩 Sending message to Letta AI: {user_message}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    try:
        response = requests.post(LETTA_API_URL, json=payload, headers=headers)
        print(f"📝 Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Error Response: {response.text}")
            return jsonify({
                "error": f"Failed to fetch recommendations, status: {response.status_code}",
                "details": response.text
            }), response.status_code

        response_json = response.json()
        print(f"🔍 API Response Data: {response_json}")

        return jsonify(response_json)  

    except requests.exceptions.RequestException as e:
        print(f"🔥 API request failed: {e}")
        return jsonify({"error": f"API request failed: {str(e)}"}), 500

@app.route('/messages', methods=['POST'])
def post_message():
    """Handle chat messages with Celeste AI"""
    payload = request.get_json()
    content = payload.get('text')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    user_message = {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }

    try:
        response = requests.post(LETTA_API_URL, json=user_message, headers=headers)
        print(f"📝 Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Error Response: {response.text}")
            return jsonify({
                "error": f"Failed to send message, status: {response.status_code}",
                "details": response.text
            }), response.status_code

        response_json = response.json()
        print(f"🔍 API Response Data: {response_json}")

        return jsonify(response_json)

    except requests.exceptions.RequestException as e:
        print(f"🔥 API request failed: {e}")
        return jsonify({"error": f"API request failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
