import csv
from datetime import datetime, timedelta
from bet_market import BetMarket
from helper import Helper 

class Autobet:
    def __init__(self, csv_predictions, csv_profiles):
        self.csv_predictions = csv_predictions
        self.csv_profiles = csv_profiles
        self.helper = Helper()

    def update_prediction(self, parent_match_id, prediction, odd):
        new_prediction = prediction.replace('OVER ', 'OV').replace('UNDER ', 'UN').replace('.', '')
        try:            
            with open(self.csv_predictions, mode='r') as csv_file:
                data = list(csv.DictReader(csv_file))

            for row in data:
                # Check if start_time is less than today and status is empty
                if row['parent_match_id'] == parent_match_id:
                    row['prediction'] = new_prediction
                    row['odd'] = odd

                # Update the CSV file with the modified data
                with open(self.csv_predictions, mode='w', newline='') as csv_file:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)

        except FileNotFoundError:
            print(f'File not found: {self.csv_predictions}')
        except Exception as e:
            print(f'An error occurred: {e}')


    def fetch_bet_markets(self, parent_match_id):
        url = f"https://api.betika.com/v1/uo/match?parent_match_id={parent_match_id}"

        try:       
            response = self.helper.fetch_data(url)
            if response is not None:
                match_details = response['data']                    
                bet_markets = [BetMarket(subtype) for subtype in match_details]

                return bet_markets

        except Exception as e:
            print(f'An error occurred: {e}')
        
        return None
    
    def get_bal(self, token):
        body = '{'
        body = body + f'''
            "token": "{token}"
        '''
        body = body + '}'

        url = f"https://api.betika.com/v1/balance"

        response = self.helper.post_data(url, body)
        data = response['data']
        return float(data['balance'])

    def place_bet(self, best_slips, profile_id, token):
        balance = self.get_bal(token)
        stakeable = balance/2
        stake = stakeable/len(best_slips)
        for bet_slip in best_slips:
            body = '{'
            body = body + f'''
                "profile_id": "{profile_id}",
                "stake": "{stake}",
                "total_odd": "1",
                "src": "MOBILE_WEB",    
                "token": "{token}",
                "betslip": [
                {bet_slip[:-1]}
                ]
            '''
            body = body + '}'

            print(body)

            url = f"https://api.betika.com/v2/bet"

            response = self.helper.post_data(url, body)
            print(response)

    def get_best_slip(self, parent_match_id, prediction):
        best_slip = None
        bet_markets = self.fetch_bet_markets(parent_match_id)
        if bet_markets is not None:
            if prediction in ['OVER', 'UNDER']:
                for bet_market in bet_markets:
                    sub_type_id = bet_market.sub_type_id
                    if sub_type_id == '18':
                        overs_market = bet_market
                        odds = overs_market.odds
                        for odd in odds:
                            if float(odd.odd_value) < 1.8 and prediction in odd.display:
                                best_slip = '{'
                                best_slip = best_slip + f'''
                                    "sub_type_id": "{sub_type_id}",
                                    "bet_pick": "{odd.odd_key}",
                                    "odd_value": "{odd.odd_value}",
                                    "outcome_id": "{odd.outcome_id}",
                                    "special_bet_value": "{odd.special_bet_value}",
                                    "parent_match_id": "{parent_match_id}",
                                    "bet_type": 7
                                '''
                                best_slip = best_slip + '}'
                                self.update_prediction(parent_match_id, odd.odd_key.upper(), odd.odd_value)

        return best_slip


    def generate_betslips(self):
        best_slips = []
        try:            
            with open(self.csv_predictions, mode='r') as csv_file:
                data = list(csv.DictReader(csv_file))
            
            bs_str = ''
            count = 0
            for row in data:
                # Check if start_time is less than today 
                try:
                    match_time = datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    match_time = datetime.strptime(row['start_time'], '%d/%m/%Y %H:%M')

                if match_time > datetime.now():
                    parent_match_id = row['parent_match_id']
                    prediction = 'OVER' if 'OV' in row['prediction'] else 'UNDER' if 'UN' in row['prediction'] else row['prediction']

                    best_slip = self.get_best_slip(parent_match_id, prediction)
                    if best_slip is not None:
                        count = count + 1
                        bs_str = bs_str + best_slip + ','

                        if count == 4:
                            best_slips.append(bs_str)   
                            count = 0 
                            bs_str = ''

            if count>0 and count < 4:
                best_slips.append(bs_str)

        except FileNotFoundError:
            print(f'File not found: {self.csv_predictions}')
        except Exception as e:
            print(f'An error occurred: {e}')

        return best_slips
    
    def __call__(self):
        """
        class entry point
        """

        best_slips = self.generate_betslips()

        try:            
            with open(self.csv_profiles, mode='r') as csv_file:
                data = list(csv.DictReader(csv_file))

            for row in data:
                profile_id = row['profile_id']
                token = row['token']
                self.place_bet(best_slips, profile_id, token)

        except FileNotFoundError:
            print(f'File not found: {self.csv_predictions}')
        except Exception as e:
            print(f'An error occurred: {e}')

        
