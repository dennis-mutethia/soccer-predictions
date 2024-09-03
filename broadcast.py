
import os, uuid, requests, random
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from utils.helper import Helper
from utils.postgres_crud import PostgresCRUD

class Broadcast():
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.sms_username = os.getenv('SMS_USERNAME')
        self.sms_password = os.getenv('SMS_PASSWORD')
        self.sender = 'M_SOURCE_SMS'
        
        self.helper = Helper()
        self.postgres_crud = PostgresCRUD()

    def yesterday_sms(self):
        matches, played, won = self.helper.fetch_matches('-1', '=')
        
        if len(matches) > 0:
            sms = f'''Yesterday our {won} of {played} Predicted Matches Won
'''
            for match in matches:
                if match.status is not None:
                    sms = sms + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

            sms = sms[:55] + f''' ...
Details - https://tipspesa.uk/yesterday/guest
Reply with 1 to get Today Sure Tips'''

            return sms.strip()  
        else:
            return None
        

    def upcoming_sms(self):
        matches, played, won = self.helper.fetch_matches('', '=', '')
        
        if len(matches) > played:
            today_codes = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).split('-')
            
            sms = f'''Today Tips
'''
            for match in matches:
                #if match.status is None:
                sms = sms + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

            sms = sms[:95] + f''' ...
All Tips - https://tipspesa.uk/{random.choice(today_codes)}'''

            return sms.strip()
        else:
            return None
    
    def send_bulk_sms_to_unsubscribed(self, sms):  
        active_subscribers = self.postgres_crud.fetch_subscribers(0)
        recipients = ''
        for subscriber in active_subscribers:
            recipients = recipients + f'{subscriber[0]},'
        
        if len(recipients) > 0:  
            print(sms) 
            encoded_sms = urllib.parse.quote(sms)
            url = f"https://bsms.smsairworks.com/smsnew/HTTP/?username={self.sms_username}&password={self.sms_password}&thread_text={encoded_sms}&thread_recievers={recipients[:-1]}&sender={self.sender}&coding=1&sms_type=promo"

            payload={}
            headers = {}

            print(url)
            
            response = requests.request("GET", url, headers=headers, data=payload)

            print(response.text)
        

    def __call__(self):
        """
        class entry point
        """

        
        sms = self.yesterday_sms()
        self.send_bulk_sms_to_unsubscribed(sms)
        
        #sms = self.upcoming_sms()
        
        #self.send_premium(sms)
        
            
if __name__ == "__main__":
    Broadcast()()