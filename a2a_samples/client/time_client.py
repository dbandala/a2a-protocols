import requests
import uuid
import json

base_url = 'http://localhost:5001'  # Change this to your server's URL if needed


# Step 1: discover the agent
res = requests.get(f'{base_url}/.well-known/agent.json')

if res.status_code != 200:
    raise Exception(f"Failed to discover agent: {res.status_code} {res.text}")

agent_info = res.json()

print("Agent discovered:")
print(json.dumps(agent_info, indent=2))

# Step 2: prepare and send a task to the agent
def send_task(task_id, message):
    """
    Sends a task to the agent and returns the response.
    """
    payload = {
        'id': task_id,
        'message': {
            'role': 'user',
            'parts': [{'text': message}],
            'metadata': {}
        }
    }
    
    response = requests.post(f'{base_url}/tasks/send', json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to send task: {response.status_code} {response.text}")



# main function to execute the client
if __name__ == '__main__':
    task_id = str(uuid.uuid4())  # Generate a unique task ID
    message = "What is the current time?"
    
    try:
        response = send_task(task_id, message)
        print("Task response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")