from __future__ import print_function
from dotenv import load_dotenv
from utils.postgres_crud import PostgresCRUD

import os
import africastalking

class Subscription:
    def __init__(self):
		# Set your app credentials
        load_dotenv()
  
        self.username = os.getenv('AT_USERNAME')
        self.api_key = os.getenv('AT_API_KEY')

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service and the Token service
        self.sms = africastalking.SMS
        self.token = africastalking.Token
                
    def create_subscription_sync(self, short_code, keyword, phone_number):
        try:
			# Get a checkoutToken for the phone number you're subscribing
            checkoutToken = self.token.create_checkout_token(phone_number)['token'] # type: ignore

            # Create the subscription
            response = self.sms.create_subscription(short_code, keyword, phone_number, checkoutToken) # type: ignore
            
            print(str(response))
            
        except Exception as e:
            print(e)

    def fetch_subscriptions_sync(self, short_code, keyword):
        # Our API will return 100 subscription numbers at a time back to you,
		# starting with what you currently believe is the last_received_id.
		# Specify 0 for the first time you access the method and the ID of
		# the last subscription we sent you on subsequent calls
  
        phone_numbers = []
        try:
            last_received_id = 0

            # Fetch all messages using a loop
            while True:
                subcription_data = self.sms.fetch_subscriptions(short_code, keyword, last_received_id) # type: ignore
                subscriptions = subcription_data['responses']
                if len(subscriptions) == 0:
                    print ('No subscription numbers.')
                    break
                for subscription in subscriptions:
                    last_received_id = subscription['id']
                    phone_number = subscription['phoneNumber']
                    print (f"{last_received_id} : {phone_number}")
                    phone_numbers.append(phone_number)
                    
		    # Note: Be sure to save the last_received_id for next time
        
        except Exception as e:
            print(e)
        
        return phone_numbers    

    
    def delete_subscription(self, short_code, keyword, phone_number):
        try:
            responses = self.sms.delete_subscription(short_code, keyword, phone_number) # type: ignore
            print (responses)
            
        except Exception as e:
            print (e)
