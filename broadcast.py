
from datetime import datetime
import uuid
from utils.helper import Helper

class Broadcast():
    def __init__(self):
        self.helper = Helper()

    def generate_sms(self, matches):
        today_code = str(uuid.uuid5(uuid.NAMESPACE_DNS, datetime.now().strftime('%Y%m%d'))).replace('-', '')[:8]
        sms = ''
        for match in matches:
            if match.status is None:
                sms = sms + f'''{match.home_team} vs {match.away_team} - {match.prediction}
'''

        sms = sms + f'''
All Tips - https://tipspesa.uk/{today_code}'''.strip()

        return sms  
        

    def __call__(self):
        """
        class entry point
        """
    
        matches, played, won = self.helper.fetch_matches('', '=', '')
        
        if len(matches) > played:
            sms = self.generate_sms(matches)
            print(sms)
        
        
if __name__ == "__main__":
    Broadcast()()