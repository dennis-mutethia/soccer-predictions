
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
        self.base_url = "https://api.betika.com"
        self.sub_types = [
            {
                "id": 1,
                "outcome_ids": [1, 2, 3]
                
            }
        ]
    
    def get_balance(self):
        url = f'{self.base_url}/v1/balance'
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
        url = f'{self.base_url}/v2/bet'
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

        try:
            # Sending the POST request
            response = requests.post(url, data=json.dumps(payload), headers=headers)

            # Print response
            print(response.json())
            
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
    
    # def compose_question(self, limit, page):        
    #     url = f'{self.base_url}/v1/uo/matches?tab=&sub_type_id=1,186,340&sport_id=14&tag_id=&sort_id=2&period_id=-1&esports=false&limit={limit}&page={page}'
    #     response = self.fetch_data(url)
    #     upcoming_matches = response.get('data')
    #     events = []
    #     for upcoming_match in upcoming_matches:
    #         home = upcoming_match.get('home_team')
    #         away = upcoming_match.get('away_team')
    #         parent_match_id = upcoming_match.get('parent_match_id')
    #         start_time = upcoming_match.get('start_time')
    #         if not ('SRL' in home or 'SRL' in away):
    #             event = {
    #                 "home_team": home,
    #                 "away_team": away,  
    #                 "parent_match_id": parent_match_id,
    #                 "start_time": start_time          
    #             }
                
    #             events.append(event)
        
    #     total = int(response.get('meta').get('total'))
    #     current_page = int(response.get('meta').get('current_page'))
    #     page = current_page + 1
        
    #     question = f'''
    #     Using data based on the available data from web sources (and tweeter feeds), team forms; kindly predict below games being played today using these markets [1, X, 2, OVER 1.5, OVER 2.5 and BOTH TEAMS TO SCORE].
    #     In each prediction give the probability in percentage. 
    #     Return as json array.
    #     {events}
    #     '''
        
    #     return total, page, question
              
    import json

    def compose_question(self, limit, page):
        url = f'{self.base_url}/v1/uo/matches?tab=&sub_type_id=1,186,340&sport_id=14&tag_id=&sort_id=2&period_id=-1&esports=false&limit={limit}&page={page}'
        response = self.fetch_data(url)
        upcoming_matches = response.get('data')
        events = []

        for upcoming_match in upcoming_matches:
            home = upcoming_match.get('home_team')
            away = upcoming_match.get('away_team')
            parent_match_id = upcoming_match.get('parent_match_id')

            if not ('SRL' in home or 'SRL' in away):
                event = {
                    "home_team": home,
                    "away_team": away,
                    "parent_match_id": parent_match_id
                }
                events.append(event)

        total = int(response.get('meta').get('total'))
        current_page = int(response.get('meta').get('current_page'))
        page = current_page + 1

        request_json = {
            "instructions": "Predict the outcome of the following football matches using available web data, including team form and Twitter feeds. Provide predictions for the following markets: 1 (Home Win), X (Draw), 2 (Away Win), Over 1.5 goals, Over 2.5 goals, and Both Teams To Score (BTTS). For each market, provide a probability percentage. Return the results as a JSON array of objects, where each object represents a match.",
            "matches": events,  # Use the 'events' list here
            "format": {
                "type": "json",
                "structure": [
                    {
                        "parent_match_id": "string",
                        "home_team": "string",
                        "away_team": "string",
                        "predictions": {
                            "BTTS": "probability",
                            "OVER 2.5": "probability",
                            "1": "probability",
                            "X": "probability",
                            "2": "probability",
                            "OVER 1.5": "probability"
                        }
                    }
                ]
            },
            "data_sources": [
                "Recent match results for the last 7 games, weighted by recency",
                "League standings",
                "Head-to-head records for the last 5 meetings",
                "Player statistics: goals and assists for key players this season, current injuries/suspensions",
                "Team news from official team websites and reputable sports news sources",
                "Expert predictions from ESPN and Sky Sports",
                "Weather forecast for the match location",
                "Home form for Team A, away form for Team B",
                "Tweets from official team accounts and reputable sports journalists covering the league",
                "Aggregate fan sentiment from Twitter (treat with caution)",
                "Team information from Wikipedia",
                "Player transfer data from Transfermarkt"
            ]
        }

        question = json.dumps(request_json)  # Convert the JSON to a string

        return total, page, question

    def generate_questions(self):
        total = 16
        limit = 15
        page = 1
        questions = []
        while limit*page < total:
            total, page, question = self.compose_question(limit, page)
            #print(question)
            questions.append(question)
            
        return questions
                    
