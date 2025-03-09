from flask import Flask, render_template, request
app = Flask(__name__)
from letta_client import Letta, MessageCreate

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/letta')
def letta():
    return render_template('letta.html')

@app.route('/questions')
def questions():
    return render_template('questions.html')

@app.route('/messages', methods=['GET'])
def messages():
    client = Letta(
        base_url="https://api.letta.com",
        token="MzQwMTljMWMtZTU4NC00MDY2LTliZGEtNDE0YTZkODY1NjlkOjc2NmIyMWJkLWFmM2UtNGVlOC1hYTg5LTkzOTAzYjE4YjE1Ng==",
    )
    messages = client.agents.messages.list(
        agent_id="agent-cb4f7fe1-a1e2-4db7-8410-227ad8180e6f",
    )
    
    
    message_array = []
    
    for message in messages:
        if message.message_type == "assistant_message" or message.message_type == "user_message":
            message_array.append({
                "id": message.id,
                "content": message.content,
                "message_type": message.message_type,
            })

    
    return message_array

@app.route('/messages', methods=['POST'])
def post_message():
    payload = request.get_json()
    content = payload.get('text')
    
    
    client = Letta(
        base_url="https://api.letta.com",
        token="MzQwMTljMWMtZTU4NC00MDY2LTliZGEtNDE0YTZkODY1NjlkOjc2NmIyMWJkLWFmM2UtNGVlOC1hYTg5LTkzOTAzYjE4YjE1Ng==",
    )
    
    
    messages = client.agents.messages.create(
        agent_id="agent-cb4f7fe1-a1e2-4db7-8410-227ad8180e6f",
        messages=[
            MessageCreate(
                role="user",
                content=content,
            )
        ],
    )
    
    message_array = []
        
    for message in messages.messages:
        if message.message_type == "assistant_message" or message.message_type == "user_message":
            message_array.append({
                "id": message.id,
                "content": message.content,
                "message_type": message.message_type,
            })

    
    return message_array

if __name__ == '__main__':
    app.run(debug=True)
