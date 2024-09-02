
import csv, argparse
from datetime import datetime
from utils.footystats.extract import Extract
from utils.postgres_crud import PostgresCRUD
from utils.predictions.goal_prediction_model import GoalPredictionModel
from utils.prep.fetch_upcoming import FetchUpcoming
from utils.prep.load_data import LoadData

class Predict:
    """
        main class
    """
    def __init__(self):
        self.csv_match_data = './data/match_data.csv' 
        self.csv_upcoming_matches = './data/upcoming_matches.csv' 
        self.csv_predictions = './docs/predictions.csv' 
        self.csv_profiles = './data/profiles.csv' 

        self.markets = ['1x2','uo','bts', 'dbc', 'ah']
        self.targets = ['ov15', 'ov25', 'gg']
        self.min_probability = 80
        self.sport_id='14'

        self.load_date = LoadData(self.csv_match_data)
        self.fetch_upcoming = FetchUpcoming(self.csv_upcoming_matches)
        self.goal_prediction_model = GoalPredictionModel()
        self.extract = Extract()
        self.postgres_crud = PostgresCRUD()

    def team_exists_in_match_data(self, team):
        """
        parameters
            team
        """
        try:
            with open(self.csv_match_data, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if team in [row['host_name'], row['guest_name']]:
                        return True
        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            pass

        return False

    def map_predicted_and_upcoming_matches(self, upcoming_matches, predicted_matches):
        """
        Method to map upcoming matches and predicted matches
        """
        mapped_predicted_matches = []
        for upcoming_match in upcoming_matches:
            upcoming_match_home_words = set(upcoming_match['home_team'].split())
            upcoming_match_away_words = set(upcoming_match['away_team'].split())

            for predicted_match in predicted_matches:
                predicted_match["prediction"] = predicted_match["prediction"].replace('GG & OV1.5', 'GG')
                predicted_match["prediction"] = predicted_match["prediction"].replace('GG & OV2.5', 'GG')
                predicted_match["prediction"] = predicted_match["prediction"].replace('1 & OV1.5', 'OV1.5')
                predicted_match["prediction"] = predicted_match["prediction"].replace('1 & OV2.5', 'OV2.5')
                predicted_match["prediction"] = predicted_match["prediction"].replace('2 & OV1.5', 'OV1.5')
                predicted_match["prediction"] = predicted_match["prediction"].replace('2 & OV2.5', 'OV1.5')
                
                predicted_match_home_words = set(predicted_match['home_team'].split())
                predicted_match_away_words = set(predicted_match['away_team'].split())

                # Check if any significant word from the home or away teams match
                home_intersection = upcoming_match_home_words & predicted_match_home_words
                away_intersection = upcoming_match_away_words & predicted_match_away_words

                if any(len(word) > 2 for word in home_intersection) and any(len(word) > 2 for word in away_intersection):
                    mapped_predicted_match = {
                        'parent_match_id': upcoming_match['parent_match_id'],
                        'sub_type_id': predicted_match['sub_type_id'],
                        'prediction': predicted_match['prediction'].split()[-1]
                    }
                    if mapped_predicted_match not in mapped_predicted_matches:
                        mapped_predicted_matches.append(mapped_predicted_match)
        
        return mapped_predicted_matches

    def last_inserted_date(self):
        """
        function to get last inserted date
        """
        # Read the CSV file and get the last row
        with open(self.csv_match_data, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            last_row = rows[-1]

        # Extract the match_day value from the last row
        return last_row[0]

    def match_results(self, home_team, away_team, match_day):
        """
        parameters
            team
        """
        host_score = None
        guest_score = None
        try:
            matches = []
            with open(self.csv_match_data, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    matches.append(row)
                
                for row in reversed(matches):                    
                    if home_team == row['host_name'] and away_team == row['guest_name'] and match_day == datetime.strptime(row['match_day'], '%Y-%m-%d').date():
                        host_score = row['host_score']
                        guest_score = row['guest_score']
                        break
                        
        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            pass

        return host_score, guest_score
    
    def update_match_status(self):
        try:            
            with open(self.csv_predictions, mode='r') as csv_file:
                data = list(csv.DictReader(csv_file))

            for row in data:
                # Check if start_time is less than today and status is empty
                if row['status'] == '':
                    try:
                        match_time = datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        match_time = datetime.strptime(row['start_time'], '%d/%m/%Y %H:%M')

                    match_day = match_time.date()
                    if match_day < datetime.now().date():  
                        status = 'LOST'                 
                        home_team = row['home_team'].title()
                        away_team = row['away_team'].title()
                        prediction = row['prediction']
                        host_score, guest_score = self.match_results(home_team, away_team, match_day)
                        
                        if host_score is not None and guest_score is not None:
                            try:
                                total_score = int(host_score) + int(guest_score)

                                if prediction=='OV15' and total_score > 1:
                                    status = 'WON'
                                elif prediction=='OV25' and total_score > 2:
                                    status = 'WON'
                                elif 'GG' in prediction and host_score > 0 and guest_score > 0:
                                    status = 'WON'
                                elif 'NG' in prediction and host_score == 0 or guest_score == 0:
                                    status = 'WON'

                            except Exception as e:
                                print(e)

                            if row['odd'] == '' and status == 'LOST':
                                status = '--'

                        else:
                            status = '--'

                        row['status'] = status
                        print(f'{match_day} {home_team} vs {away_team} : {host_score} - {guest_score} : {prediction} : {status}')

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

    def predict_upcoming_matches(self):
        """
        method to predict upcoming matches
        """
        try:
            with open(self.csv_upcoming_matches, mode='r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    start_time = row['start_time']
                    parent_match_id = row['parent_match_id']
                    home_team = row['home_team'].title()
                    away_team = row['away_team'].title()
                    if self.team_exists_in_match_data(home_team) and self.team_exists_in_match_data(away_team):
                        for target in self.targets:
                            try:
                                self.goal_prediction_model(self.csv_match_data, start_time, parent_match_id, home_team, away_team, target, self.min_probability)
                            except ValueError as ex:
                                print(f"An error occurred: {ex}")
                                # Continue with the next iteration of the loop
                                continue

        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            pass
        
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
                
                status = 'LIVE' if live else status
                #print(f'prediction={prediction} home_results={home_results} away_results={away_results} status={status}')
                self.postgres_crud.update_match_results(match_id, home_results, away_results, status)
           
    def __call__(self, autobet):
        """
        class entry point
        """

        upcoming_matches = self.fetch_upcoming(self.sport_id)

        predicted_matches = self.extract()
        
        for match in predicted_matches:
            self.postgres_crud.insert_match(match)
        
        mapped_predicted_matches = self.map_predicted_and_upcoming_matches(upcoming_matches, predicted_matches)  
        
        if int(autobet) == 1:       
            Autobet(mapped_predicted_matches, self.csv_profiles)()
        
        self.update_results()
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--autobet", type=int, required=True, help="an integer value for x")
    
    args = parser.parse_args()
    Predict()(args.autobet)