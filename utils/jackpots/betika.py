
import requests

from utils.entities import Event, Jackpot, Odds

class Betika():
    def __init__(self):
        self.base_url = "https://api.betika.com/v1/jackpot"
        
        #https://api.betika.com/v1/jackpot/event?id=2419
     
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
    
    def get_jackpot_selections(self):        
        url = f'{self.base_url}/events'
        data = self.fetch_data(url)
        jackpots = []
        for datum in data: 
            id = datum["id"]
            title = f'{datum["event_name"]} (BETIKA)'
            url = f'{self.base_url}/event?id={id}'
            response = self.fetch_data(url)
        
            events = []
            data_ = response["data"]
            for datum_ in data_:
                event_id = datum_["parent_match_id"]
                home = datum_["home_team"]
                away = datum_["away_team"]
                start_time = datum_["start_time"]
                
                odds = []
                home_odds = draw_odds = away_odds = 1
                for odd in datum_["odds"]:
                    home_odds = odd["odd_value"] if odd["display"] == "1" else home_odds
                    draw_odds = odd['odd_value'] if odd["display"] == "X" else draw_odds
                    away_odds = odd['odd_value'] if odd["display"] == "2" else away_odds
                
                odds.append(Odds(home_odds, draw_odds, away_odds))
                events.append(Event(event_id, start_time, home, away, odds))    
                    
            jackpots.append(Jackpot(id, title, events)) 
        
        return jackpots
    