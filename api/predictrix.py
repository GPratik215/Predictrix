import random
import json
from datetime import datetime, timedelta
import requests  # For sending HTTP requests

# Simulate data
users = [f'user{num}' for num in range(1, 101)]  # 100 users
events = ['Add to Cart', 'Page View', 'Login', 'Logout']
devices = ['Mobile', 'Desktop', 'Tablet']
locations = ['New York', 'London', 'Mumbai', 'Tokyo', 'Sydney']
pages = ['Home', 'Product Page', 'Cart', 'Checkout']

# Create a function to generate random logs
def generate_log():
    user_id = random.choice(users)
    event = random.choice(events)
    timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # Random time within the last day
    timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S")
    device = random.choice(devices)
    location = random.choice(locations)
    page = random.choice(pages)
    
    log = {
        "user_id": user_id,
        "event": event,
        "timestamp": timestamp,
        "device": device,
        "location": location,
        "page": page
    }
    return log

# Function to send the logs to Splunk
def send_to_splunk(log):
    # url = "https://127.0.0.1:8088/services/collector"  # Replace with your Splunk server URL
    url = "https://host.docker.internal:8088/services/collector"

    headers = {
        'Authorization': 'Splunk 2315ad94-e6ae-42c6-a2a4-20aeba6568be',  # Replace <your-hec-token> with your token
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps({"event": log}), verify=False)
    return response.status_code

# Generate and send logs in bulk
for _ in range(10):  # Generate 10 random logs
    log = generate_log()
    status = send_to_splunk(log)
    print(f"Log sent with status code: {status}")

