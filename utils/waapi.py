import os, requests
from dotenv import load_dotenv

class WaAPI:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        instance_id = os.getenv('WAAPI_INSTANCE_ID')
        token = os.getenv('WAAPI_TOKEN')
        
        self.base_url = f"https://waapi.app/api/v1/instances/{instance_id}/client/action"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }

    def send_message(self, phone_number, message):
        url = f"{self.base_url}/send-message"
        payload = {
            "chatId": f"{phone_number}@c.us",
            "message": message
            #"mentions": ["{phone_number}@c.us", "987654321@c.us"],
            #"replyToMessageId": "<bool>_<xxxxx>@c.us>_<megssageHash>"
        }
        
        response = requests.post(url, json=payload, headers=self.headers)

        return response.json()
        
        