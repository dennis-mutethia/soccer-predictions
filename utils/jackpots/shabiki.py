
import requests

from utils.entities import JackpotSelections

class Shabiki():
    def __init__(self):
        self.base_url = "https://fapi.shabiki.com/sportjackpots"
        
    def fetch_data(self):
        url = f'{self.base_url}'
        
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
        jackpots = []
        response = self.fetch_data()
        data = response["params"]["jackpots"]
        for datum in data:
            if datum["status"] == 1:
                id = datum["id"]
                for event in datum["events"]:
                    event_id = event["id"]
                    event_start_date = event["event_start_date"]
                    home = event["home"]
                    away = event["away"]
                    home_odds = draw_odds = away_odds = 1
                    for selection in event["selections"]:
                        home_odds = selection['odd'] if selection["name"] == "1" else home_odds
                        draw_odds = selection['odd'] if selection["name"] == "X" else draw_odds
                        away_odds = selection['odd'] if selection["name"] == "2" else away_odds
                
                    jackpot_selection = JackpotSelections(id, event_id, event_start_date, home, away, home_odds, draw_odds, away_odds)
                    print(f"{jackpot_selection.id} - {jackpot_selection.event_id} - {jackpot_selection.start_date} - {jackpot_selection.home} vs {jackpot_selection.away} : {jackpot_selection.home_odds} - {jackpot_selection.draw_odds} - {jackpot_selection.away_odds}") 
                    jackpots.append(jackpot_selection)
            
        return jackpots
    