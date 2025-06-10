from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# define endpoint for agent card - discovery phase
@app.route('/.well-known/agent.json', methods=['GET'])
def agent_card():
    """
    Endpoint to return the agent card information.
    """
    agent_info = {
        'name': 'Time Teller',
        'description': 'An agent that tells the current time based on the provided timezone.',
        'url': 'http://localhost:5000/tell_time',
        'capabilities': {
            'streaming': False,
            'pushNotifications': False,
        },
        'version': '1.0.0'
    }
    return jsonify(agent_info)

# define enfpoint for task handling - task/send
@app.route('/tasks/send', methods=['POST'])
def handle_task():
    """
    Endpoint to handle tasks sent to the agent.
    Expects a JSON payload with a 'task' key.
    """
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Invalid JSON format'}), 400
    if request.json is None:
        return jsonify({'status': 'error', 'message': 'Request body is empty'}), 400
    data = request.get_json()

    try:
        task_id = data['id']  # Extracting the task ID from the request
        #task = data['task']
        user_message = data['message']['parts'][0]['text']
    except (KeyError, IndexError, TypeError) as e:
        return jsonify({'status': 'error', 'message': f'Invalid task format: {str(e)}'}), 400
    
    # generate response to user message
    # get the current time as formatted string
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reply_text = f"Current time is: {current_time}"

    response = {
        'status': 'success',  # Indicating the task was processed successfully
        'id': task_id, # Echoing back the task ID
        'messages': [
            data['message'], # Echoing back the original message
            {
                'role': 'agent',  # Indicating this is a response from the agent
                'parts': [{'text': reply_text}],  # The agent's reply
                'metadata': {}  # Additional metadata can be added here if needed
            }
        ]
    }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Run the Flask app on all interfaces, port 5000, with debug mode enabled