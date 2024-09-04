
import os, requests
import urllib.parse

from dotenv import load_dotenv

class PremiumSMS:
    def __init__(self):
		# Set your app credentials
        load_dotenv()

        self.url = os.getenv('AT_URL')
        self.username = os.getenv('AT_USERNAME')
        self.api_key = os.getenv('AT_API_KEY')
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'apiKey': self.api_key
        }
    
    def send(self, shortcode, keyword, recipients, message): 
        recipients = urllib.parse.quote_plus(recipients)
        message = urllib.parse.quote_plus(message)
        
        payload = f'username={self.username}&from={shortcode}&keyword={keyword}&to={recipients}&message={message}'
        print(payload)
        
        try:
            response = requests.request("POST", self.url, headers=self.headers, data=payload)
            print(response.text)
            
            return response.json()
            
        except Exception as err:
            print(f"An error occurred: {err}")
            return None
