
from datetime import datetime
import uuid
from utils.helper import Helper

class Broadcast():
    def __init__(self):
        self.helper = Helper()

    def yesterday_sms(self):
        matches, played, won = self.helper.fetch_matches('-1', '=')
        
        if len(matches) > 0:
            today_code = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).replace('-', '')[:8]
            sms = f'''
Yesterday our {won} of {played} predicted matches won
'''
            for match in matches:
                sms = sms + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

            sms = sms[:160] + f'''
https://tipspesa.uk/yesterday/{today_code}
Reply with 1 to get Today Sure Tips'''

            print(sms)
            return sms  
        else:
            return None
        

    def upcoming_sms(self):
        matches, played, won = self.helper.fetch_matches('', '=', '')
        
        if len(matches) > played:
            today_code = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).replace('-', '')[:8]
            sms = ''
            for match in matches:
                if match.status is None:
                    sms = sms + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

            sms = sms[:200] + f'''
All Tips - https://tipspesa.uk/{today_code}'''

            print(sms)
            return sms  
        else:
            return None
        

    def __call__(self):
        """
        class entry point
        """
    
        sms = self.yesterday_sms()
        #sms = self.upcoming_sms()
        
        
if __name__ == "__main__":
    Broadcast()()