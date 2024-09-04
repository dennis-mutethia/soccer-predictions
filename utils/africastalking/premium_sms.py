
import os, requests
import urllib.parse

from dotenv import load_dotenv

class PremiumSMS:
    def __init__(self):
		# Set your app credentials
        load_dotenv()

        self.token_url = os.getenv('AT_TOKEN_URL')
        self.subscription_url = os.getenv('AT_SUBSCRIPTION_URL')
        self.content_url = os.getenv('AT_CONTENT_URL')
        self.username = os.getenv('AT_USERNAME')
        self.api_key = os.getenv('AT_API_KEY')
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'apiKey': self.api_key
        }
    
    def subscribe(self, shortcode, keyword, phone_number): 
        phone_number = urllib.parse.quote_plus(phone_number)
        
        payload = f'phoneNumber={phone_number}'
        print(payload)
        
        try:
            response = requests.request("POST", self.token_url, headers=self.headers, data=payload)
            checkoutToken = response.json()["token"]
            print(checkoutToken)
            
            payload = f'username={self.username}&shortCode={shortcode}&keyword={keyword}&phoneNumber={phone_number}&checkoutToken={checkoutToken}'
            print(payload)
            response = requests.request("POST", self.subscription_url, headers=self.headers, data=payload)
            print(response.text)

            return response.json()
            
        except Exception as err:
            print(f"An error occurred: {err}")
            return None
    
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
