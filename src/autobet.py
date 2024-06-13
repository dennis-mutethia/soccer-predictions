import uuid, csv, time, math, concurrent.futures
from bet_market import BetMarket
from helper import Helper 
from utils.postgres_crud import PostgresCRUD

class Autobet:
    def __init__(self, matches, csv_profiles):
        self.matches = matches
        self.csv_profiles = csv_profiles
        self.helper = Helper()
        self.match_ids = []
        self.postgres_crud = PostgresCRUD()

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
        stakeable = balance * 0.5
        if int(stakeable) > 0:
            stake = math.ceil(stakeable/len(best_slips))
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

                #response = self.helper.post_data(url, body)
                #print(response)
                time.sleep(10)

            for match_id in self.match_ids:
                self.postgres_crud.insert_betslip(match_id, profile_id)
            
    def get_best_slip(self, match):
        best_slip = None
        bet_markets = self.fetch_bet_markets(match['parent_match_id'])
        if bet_markets is not None:
            for bet_market in bet_markets:
                sub_type_id = bet_market.sub_type_id
                if int(sub_type_id) == int(match['sub_type_id']):
                    odds = bet_market.odds
                    for odd in odds:
                        prediction = match['prediction'].split()[-1]   
                        if prediction in odd.display:
                            best_slip = '{'
                            best_slip = best_slip + f'''
                                "sub_type_id": "{sub_type_id}",
                                "bet_pick": "{odd.odd_key}",
                                "odd_value": "{odd.odd_value}",
                                "outcome_id": "{odd.outcome_id}",
                                "special_bet_value": "{odd.special_bet_value}",
                                "parent_match_id": "{match['parent_match_id']}",
                                "bet_type": 7
                            '''
                            best_slip = best_slip + '}'
                            
                            match["odd"] = odd.odd_value
                            
                            return best_slip

    def generate_betslips(self):
        best_slips = []
        bs_str = ''
        count = 0
        total_odd = 1
        for match in self.matches:            
            best_slip = self.get_best_slip(match)            
            
            if best_slip is not None:
                count = count + 1
                bs_str = bs_str + best_slip + ','
                total_odd = total_odd * float(match["odd"])
                
                match_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{match['start_time']}{match['home_team']}{match['away_team']}"))
                is_placed = self.postgres_crud.is_placed(match_id) 
                
                if not is_placed:
                    self.match_ids.append(match_id)

                    if total_odd >= 4.0:
                        best_slips.append(bs_str)
                        total_odd = 1
                        bs_str = ''

        if total_odd > 1:
            best_slips.append(bs_str)
                    
        return best_slips
    
    def __call__(self):
        """
        class entry point
        """

        best_slips = self.generate_betslips()
        
        try:            
            with open(self.csv_profiles, mode='r') as csv_file:
                data = list(csv.DictReader(csv_file))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                threads = [executor.submit(self.place_bet, best_slips, row['profile_id'], row['token']) for row in data]

                # Wait for all threads to complete
                concurrent.futures.wait(threads)

        except FileNotFoundError:
            print(f'File not found: {self.csv_profiles}')
        except Exception as e:
            print(f'An error occurred: {e}')

        
