import requests
from datetime import datetime

# Replace with your actual API token
api_token = "KE6gjLLwBerKPuWkqDbG3OszRw9dLCKcNpQnciBwekP9fUWmA87nVoyowUqJ"

# URL of the API endpoint
url = "https://api.leadcraft.ru/v1/webmasters/lead"

# Construct the data payload
data = {
    "type": "lead",
    "api_token": api_token,
    "applied_at": datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    ),  # Current date and time in the required format
    "sales": [
        {"campaignID": "campaign_id_1"},
        {"campaignID": "campaign_id_2"},
        # Add more campaign IDs as needed
    ],
}

# Send the POST request
response = requests.post(url, json=data, headers={"Content-Type": "application/json"})

# Check the response
if response.status_code == 200:
    print("Lead submitted successfully:", response.json())
else:
    print("Failed to submit lead:", response.status_code, response.text)
