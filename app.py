from flask import Flask, render_template, request, jsonify
from letta_client import Letta, MessageCreate

app = Flask(__name__)

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
    user_message = user_data.get("messages")[0]["content"]

    client = Letta(
        base_url="https://api.letta.com",
        token="MzQwMTljMWMtZTU4NC00MDY2LTliZGEtNDE0YTZkODY1NjlkOjc2NmIyMWJkLWFmM2UtNGVlOC1hYTg5LTkzOTAzYjE4YjE1Ng==",
    )

    # API request to Letta AI
    messages = client.agents.messages.create(
        agent_id="agent-cb4f7fe1-a1e2-4db7-8410-227ad8180e6f",
        messages=[
            MessageCreate(
                role="user",
                content=user_message
            )
        ],
    )

    message_array = []

    for message in messages.messages:
        if message.message_type == "assistant_message":
            message_array.append({
                "content": message.content,
                "message_type": message.message_type,
            })

    return jsonify({"messages": message_array})

if __name__ == '__main__':
    app.run(debug=True)
