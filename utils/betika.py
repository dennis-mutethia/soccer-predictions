
import json
import os
from dotenv import load_dotenv
import requests

from utils.grok import Grok

load_dotenv()   
BETIKA_PROFILE_ID = os.getenv("BETIKA_PROFILE_ID")
BETIKA_TOKEN = os.getenv("BETIKA_TOKEN")

class Betika():
    def __init__(self):
        self.base_url = "https://api.betika.com/v1/uo/matches?tab=&sub_type_id=1,186,340&sport_id=14&tag_id=&sort_id=1&period_id=-1&esports=false"
        self.sub_types = [
            {
                "id": 1,
                "outcome_ids": [1, 2, 3]
                
            }
        ]
    
    def get_balance(self):
        url = 'https://api.betika.com/v1/balance'
        payload = {
            "profile_id": str(BETIKA_PROFILE_ID),
            "src": "MOBILE_WEB",
            "token": BETIKA_TOKEN,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "app_version": "6.0.0"
        }
                        
        headers = {"Content-Type": "application/json"}

        # Sending the POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        # Print response
        data = response.json().get('data')
        return data.get('balance'), data.get('bonus')        
       
    def place_bet(self, betslips, total_odd, stake):
        url = 'https://api.betika.com/v2/bet'
        payload = {
            "profile_id": str(BETIKA_PROFILE_ID),
            "stake": str(stake),
            "total_odd": str(total_odd),
            "src": "MOBILE_WEB",
            "betslip": betslips,
            "token": BETIKA_TOKEN,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "app_version": "6.0.0",
            "affiliate": None,
            "promo_id": None,
            "fbpid": False,
            "is_freebet": False
        }
                        
        headers = {"Content-Type": "application/json"}

        # Sending the POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        # Print response
        print(response.json())
        
                 
    def fetch_data(self, url):   
        try:
            response = requests.get(url)
            
            response.raise_for_status()  # Raises an HTTPError if the response status code indicates an error
            return response.json()  # Assuming the response is JSON
        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")
        except Exception as err:
            print(f"Unexpected error: {err}")
    
    def compose_question(self, limit, page):        
        url = f'{self.base_url}&limit={limit}&page={page}'
        response = self.fetch_data(url)
        upcoming_matches = response.get('data')
        events = []
        for upcoming_match in upcoming_matches:
            home = upcoming_match.get('home_team')
            away = upcoming_match.get('away_team')
            parent_match_id = upcoming_match.get('parent_match_id')
            start_time = upcoming_match.get('start_time')
            if not ('SRL' in home or 'SRL' in away):
                event = {
                    "home_team": home,
                    "away_team": away,  
                    "parent_match_id": parent_match_id,
                    "start_time": start_time          
                }
                
                events.append(event)
        
        total = int(response.get('meta').get('total'))
        current_page = int(response.get('meta').get('current_page'))
        page = current_page + 1
        
        question = f'''
        Using data based on the available data from web sources (and tweeter feeds), team forms; kindly predict below games being played today using these markets [1, X, 2, OVER 1.5, OVER 2.5 and BOTH TEAMS TO SCORE].
        In each prediction give the probability in percentage. 
        Return as json array.
        {events}
        '''
        
        return total, page, question
              
    def generate_messages(self):
        total = 21
        limit = 20
        page = 1
        
        while limit*page < total:
            total, page, question = self.compose_question(limit, page)
            print(question)
                    
