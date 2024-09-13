
import os, uuid, random
from dotenv import load_dotenv
from datetime import datetime
from utils.helper import Helper
from utils.postgres_crud import PostgresCRUD
from utils.safaricom.exceptions.sdp_exception import SDPException
from utils.safaricom.premium_sms import PremiumSMS
from utils.safaricom.sdp import SDP

load_dotenv()

class Broadcast():
    def __init__(self):        
        self.helper = Helper()
        self.postgres_crud = PostgresCRUD()

    def send_welcome_message(self, phone):        
        message = '''Welcome to *TipsPesa Sure Predictions*.
We will send you our Predictions everyday.
Additionally, there will be a unique link to view all predicted games for that day.

N/B: The received link expires after 24hrs - So, each day, you will use the new link sent on that particular day.

Terms and conditions apply. Bet responsibly'''

        self.send_premium_sms(phone, message)
                
    def yesterday_message(self):
        matches, played, won = self.helper.fetch_matches('-1', '=')
        
        if len(matches) > 0:
            message = f'''Yesterday {won} of {played} Predicted Matches Won
         
'''
            for match in matches:
                if match.status is not None:
                    message = message + f'''{match.home_team} vs {match.away_team} - {match.prediction} [{match.home_results}-{match.away_results}]'''

            message = message[:150] + '''...
    
Details - https://tipspesa.uk/yesterday/guest

Reply with "1" to get Sure Predictions daily'''

            return message.strip()  
        else:
            return None
        

    def upcoming_message(self):
        matches, played, won = self.helper.fetch_matches('', '=', '')
        
        if len(matches) > played:
            today_codes = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).split('-')
            
            message = '''Today Predictions
'''
            for match in matches:
                #if match.status is None:
                message = message + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

            message = message[:120] + f'''...

All Tips - https://tipspesa.uk/{random.choice(today_codes)}

New Predictions added every hour. Just Refresh above Link for Latest Predictions
STOP *456*20#'''

            return message.strip()
        else:
            return None
    
    def send_predictions_to_subscribed(self, message):  
        # Step 1: Fetch active subscribers
        active_subscribers = self.postgres_crud.fetch_subscribers(1, sms=True)
        
        # Step 2: Extract phone numbers and join them as comma-separated values
        recipients = ",".join([subscriber[0] for subscriber in active_subscribers])
        
        # Optional: Debugging to see the recipients list
        print(f"Sending SMS to: {recipients}")
        
        self.send_premium_sms(recipients, message)

    def send_premium_sms(self, phone_number, message):
        try:
            # Instantiate the SDP class, passing the API username, password, and cp_id
            sdp = SDP()

            # By default, SDP will use sandbox APIs. Call use_live() method to use production APIs.
            sdp.use_live().init()

            # Instantiate the PremiumSMS class and pass the SDP instance
            premium_sms = PremiumSMS(sdp)

            # Send SMS
            request_id = f"{phone_number}-{datetime.now().strftime('%d')}"  # Generate an ID for tracking/logging purposes
            offer_code = os.getenv('PREMIUM_SMS_OFFER_CODE')  # 21155 The service for which the SMS is being sent
            
            response = premium_sms.send_sms(request_id, offer_code, phone_number, message)
            
            print(response)

        except SDPException as ex:
            # Handle error logging here, most likely exceptions occur during token generation
            print(ex)
    
    def __call__(self):
        """
        class entry point
        """
        
        #message = self.yesterday_message()
        
        message = self.upcoming_message()
        self.send_predictions_to_subscribed(message)        
            
if __name__ == "__main__":
    Broadcast()()