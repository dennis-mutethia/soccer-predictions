
import os, uuid, requests, random
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from utils.helper import Helper
from utils.postgres_crud import PostgresCRUD

class Broadcast():
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.sms_username = os.getenv('SMS_USERNAME')
        self.sms_password = os.getenv('SMS_PASSWORD')
        self.bulk_base_url = 'https://kenyasms.rpdigitalphone.com/smsnew/HTTP/'
        self.bulk_sender = 'M_SOURCESMS'
        
        self.helper = Helper()
        self.postgres_crud = PostgresCRUD()

    def subscribe(self, phone):
        self.postgres_crud.update_subscriber_on_opt(phone, 1) 
        
        sms = '''Welcome to TipsPesa Sure Betting Tips.
We will send TIPS everyday with a unique link to view all predicted games.
Terms and conditions apply.'''

        print(sms) 
        encoded_sms = urllib.parse.quote(sms)
        url = f"{self.bulk_base_url}?username={self.sms_username}&password={self.sms_password}&thread_text={encoded_sms}&thread_recievers={recipients[:-1]}&sender={self.bulk_sender}&coding=1&sms_type=trans"

        payload={}
        headers = {}

        print(url)
        
        response = requests.request("GET", url, headers=headers, data=payload)
        print(response)
        
    def yesterday_sms(self):
        matches, played, won = self.helper.fetch_matches('-1', '=')
        
        if len(matches) > 0:
            sms = f'''Yesterday our {won} of {played} Predicted Matches Won
'''
            for match in matches:
                if match.status is not None:
                    sms = sms + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

            sms = sms[:55] + ''' ...
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
            url = f"{self.bulk_base_url}?username={self.sms_username}&password={self.sms_password}&thread_text={encoded_sms}&thread_recievers={recipients[:-1]}&sender={self.bulk_sender}&coding=1&sms_type=trans"

            payload={}
            headers = {}

            print(url)
            
            response = requests.request("GET", url, headers=headers, data=payload)  
            print(response.text)
            
            #self.update_db_on_send(recipients, response)         
    
    def send_premium_sms_to_subscribed(self, sms):  
        active_subscribers = self.postgres_crud.fetch_subscribers(1)
        recipients = ''
        for subscriber in active_subscribers:
            recipients = recipients + f'{subscriber[0]},'
        
        if len(recipients) > 0:  
            print(sms) 
            encoded_sms = urllib.parse.quote(sms)
            url = f"{self.bulk_base_url}?username={self.sms_username}&password={self.sms_password}&thread_text={encoded_sms}&thread_recievers={recipients[:-1]}&sender={self.bulk_sender}&coding=1&sms_type=trans"

            payload={}
            headers = {}

            print(url)
            
            response = requests.request("GET", url, headers=headers, data=payload)
            print(response.text)
            
            self.update_db_on_send(recipients, response)
    
    def update_db_on_send(self, recipients, response):

        # Parse the XML
        root = ET.fromstring(response.text)

        # Extract guid and submitdate
        smsguid_element = root.find('smsguid')
        if smsguid_element is not None:
            guid_value = smsguid_element.get('guid')
            submitdate_value = smsguid_element.get('submitdate')
            self.postgres_crud.update_subscriber_on_send(recipients[:-1], guid_value, submitdate_value)
       
    def __call__(self):
        """
        class entry point
        """

        
        #sms = self.yesterday_sms()
        #self.send_bulk_sms_to_unsubscribed(sms)
        
        sms = self.upcoming_sms()
        self.send_premium_sms_to_subscribed(sms)
        
        
            
if __name__ == "__main__":
    Broadcast()()