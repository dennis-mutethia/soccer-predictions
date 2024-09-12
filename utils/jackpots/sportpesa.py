
import requests

from utils.entities import Event, Jackpot, Odds


class Sportpesa():
    def __init__(self):
        self.base_url = "https://jackpot-offer-api.ke.sportpesa.com/api/jackpots"
     
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
        url = f'{self.base_url}/active'
        data = self.fetch_data(url)
        jackpots = []
        if data is not None:   
            id = data["humanId"]
            title = f'{data["settings"]["numberOfEvents"]} Games Jackpot (SPORTPESA)'
            events = []         
            for event in data["events"]:
                event_id = event["id"].replace("sr:match:", "")
                start_time = event["utcKickOffTime"]
                bettingStatus = event["bettingStatus"]
                odds = []
                if bettingStatus == "Open":
                    for competitor in event["competitors"]:
                        if competitor["isHome"]:
                            home = competitor["competitorName"]
                        else:
                            away = competitor["competitorName"]
                            
                    home_odds = event["home"]
                    draw_odds = event["draw"]
                    away_odds = event["away"]
                    odds.append(Odds(home_odds, draw_odds, away_odds))
                    events.append(Event(event_id, start_time, home, away, odds))   
            jackpots.append(Jackpot(id, title, events))        
        
        return jackpots
    