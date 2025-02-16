
import json, time

from numpy import double
from utils.betika import Betika
from utils.postgres_crud import PostgresCRUD

class AutoBet():
    def __init__(self) -> None:
        self.betika = Betika()     
        self.db = PostgresCRUD()
    
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
        min_odd = 10
        total_odd = 1
        composite_betslip = None
        composite_betslips = []
        # Load JSON data from a file
        with open('predictions.json', 'r') as file:
            data = json.load(file)
            added_parent_match_ids = set()
            for datum in data:
                parent_match_id= datum.get('parent_match_id')
                predictions = datum.get('predictions')
                for key in predictions:
                    prediction = predictions.get(key)
                    #key = key.replace('BTTS','YES')
                    prediction = prediction if isinstance(prediction, int) else double(prediction.replace('%', ''))
                    if (key == 'OVER 2.5' and prediction>=75) or (key=='OVER 1.5' and prediction>=85):  
                        url = f'https://api.betika.com/v1/uo/match?parent_match_id={parent_match_id}'
                        match_details = self.betika.fetch_data(url)
                        data = match_details.get('data')
                        if data:
                            for d in data:
                                sub_type_id = d.get('sub_type_id')
                                if sub_type_id in ["18"]:
                                    odds = d.get('odds')
                                    for odd in odds:
                                        odd_value = odd.get('odd_value')
                                        if key == odd.get('display') and double(odd_value)>=1.2 and double(odd_value)<=1.6 and parent_match_id not in added_parent_match_ids:
                                            bet_pick = odd.get('odd_key')
                                            special_bet_value = odd.get('special_bet_value')
                                            outcome_id = odd.get('outcome_id')
                                            betslip = self.compose_bet_slip(parent_match_id, sub_type_id, bet_pick, odd_value, outcome_id, special_bet_value)
                                            betslips.append(betslip)
                                            print(f"{datum.get('home_team')} vs {datum.get('away_team')} = {key} [x{odd_value}]")
                                            added_parent_match_ids.add(parent_match_id)
                                            total_odd *= double(odd_value)                                            
                                            composite_betslip = {
                                                'total_odd': total_odd,
                                                'betslips': betslips
                                            }
                                            if total_odd > min_odd:
                                                composite_betslips.append(composite_betslip)
                                                betslips = []
                                                total_odd = 1
                                                composite_betslip = None 
                                            match = {
                                                'match_id': match_details.get('meta').get('match_id'),
                                                'start_time': match_details.get('meta').get('start_time'),
                                                'home_team': datum.get('home_team'),
                                                'away_team': datum.get('away_team'),
                                                'prediction': key if key != 'YES' else 'GG',
                                                'odd': odd_value,
                                                'overall_prob': prediction
                                            }
                                            self.db.insert_match(match)
            if composite_betslip:
                composite_betslips.append(composite_betslip)
            if len(composite_betslips) > 0:                        
                balance, bonus = self.betika.get_balance()
                placeable = (balance+bonus) #*0.75
                min_stake = placeable/min_odd
                equal_stake = placeable/len(composite_betslips)
                max_stake = max(min_stake, equal_stake)
                stake = int( max_stake if max_stake>1 else placeable)
                #stake = round(equal_stake)
                if stake > 0:
                    for cb in composite_betslips:
                        ttl_odd = cb['total_odd']
                        slips = cb['betslips']
                        print(f'TOTAL ODD: {ttl_odd}')
                        self.betika.place_bet(slips, ttl_odd, stake)
                        time.sleep(5)
             
if __name__ == '__main__':
    AutoBet()()