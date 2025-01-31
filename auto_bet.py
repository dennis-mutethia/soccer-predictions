
import json

from numpy import double
from utils.betika import Betika

class AutoBet():
    def __init__(self) -> None:
        self.betika = Betika()
    
    def compose_bet_slip(self, parent_match_id, sub_type_id, bet_pick, odd_value, outcome_id, special_bet_value):
        return {
            "sub_type_id": str(sub_type_id),
            "bet_pick": bet_pick, #team
            "odd_value": odd_value,
            "outcome_id": str(outcome_id),  
            "sport_id": "14",
            "special_bet_value": special_bet_value,
            "parent_match_id": str(parent_match_id),
            "bet_type": 7
        }
    
    def __call__(self):
        betslips = []
        total_odd = 1
        # Load JSON data from a file
        with open('predictions.json', 'r') as file:
            data = json.load(file)
            for datum in data:
                parent_match_id= datum.get('parent_match_id')
                predictions = datum.get('predictions')
                for key in predictions.keys():
                    prediction = predictions.get(key)
                    if prediction >= 75:  
                        url = f'https://api.betika.com/v1/uo/match?parent_match_id={parent_match_id}'
                        match_details = self.betika.fetch_data(url)
                        data = match_details.get('data')
                        for d in data:
                            sub_type_id = d.get('sub_type_id')
                            odds = d.get('odds')
                            for odd in odds:
                                odd_value = odd.get('odd_value')
                                if key == odd.get('display').replace(' (GG/NG)', '') and double(odd_value)<1.5:
                                    bet_pick = odd.get('odd_key')
                                    special_bet_value = odd.get('special_bet_value')
                                    outcome_id = odd.get('outcome_id')
                                    betslip = self.compose_bet_slip(parent_match_id, sub_type_id, bet_pick, odd_value, outcome_id, special_bet_value)
                                    betslips.append(betslip)
                                    total_odd = total_odd * double(odd_value)
                                    
                        break  

        stake = 3
        self.betika.place_bet(betslips, total_odd, stake)
             
if __name__ == '__main__':
    AutoBet()()