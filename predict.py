
from utils.footystats.extract import Extract
from utils.postgres_crud import PostgresCRUD

class Predict:
    """
        main class
    """
    def __init__(self):
        self.extract = Extract()
        self.postgres_crud = PostgresCRUD()

    def update_results(self):
        open_matches = self.postgres_crud.fetch_open_matches()
        for match in open_matches:  
            match_id = match[0] 
            kickoff = match[1] 
            prediction = match[4] 
            match_url = match[6].replace("*","#")
            print(f'match_id={match_id} kickoff={kickoff} prediction={prediction} match_url={match_url}')
            home_results, away_results, live = self.extract.fetch_results(match_url, kickoff)   
            if home_results is not None and (home_results != 0 or away_results != 0):
                status = 'LOST'
                total_goals = home_results + away_results
                if prediction == 'HOME WIN' and home_results>away_results:
                    status = 'WON'
                if prediction == 'AWAY WIN' and away_results>home_results:
                    status = 'WON'
                if prediction == 'TOTAL OVER 3.5' and total_goals>3:
                    status = 'WON'
                if prediction == 'TOTAL OVER 2.5' and total_goals>2:
                    status = 'WON'
                if prediction == 'TOTAL OVER 1.5' and total_goals>1:
                    status = 'WON'
                    
                if prediction == 'HOME TOTAL OVER 1.5' and home_results>1:
                    status = 'WON'
                if prediction == 'AWAY TOTAL OVER 1.5' and away_results>1:
                    status = 'WON'
                if prediction == 'HOME TOTAL OVER 0.5' and home_results>0:
                    status = 'WON'
                if prediction == 'AWAY TOTAL OVER 0.5' and away_results>0:
                    status = 'WON'  
                    
                if prediction == 'BOTH TEAMS TO SCORE' and home_results>0 and away_results>0:
                    status = 'WON'  
                    
                                  
                
                status = 'LIVE' if live else status
                #print(f'prediction={prediction} home_results={home_results} away_results={away_results} status={status}')
                self.postgres_crud.update_match_results(match_id, home_results, away_results, status)
           
    def __call__(self):
        """
        class entry point
        """

        predicted_matches = self.extract()
        
        for match in predicted_matches:
            self.postgres_crud.insert_match(match)
        
        self.update_results()
  
if __name__ == "__main__":
    Predict()()