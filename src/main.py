import csv
from datetime import datetime, timedelta
from prep.load_data import LoadData
from prep.fetch_upcoming import FetchUpcoming
from predictions.goal_prediction_model import GoalPredictionModel

class Main:
    """
        main class
    """
    def __init__(self):
        self.csv_match_data = './data/match_data.csv' 
        self.csv_upcoming_matches = './data/upcoming_matches.csv' 
        self.csv_predictions = './docs/predictions.csv' 
        self.markets = ['1x2','uo','bts'] 
        self.targets = ['ov15', 'ov25', 'gg']
        self.min_probability = 80
        self.sport_id='14'

        self.load_date = LoadData(self.csv_match_data)
        self.fetch_upcoming = FetchUpcoming(self.csv_upcoming_matches)
        self.goal_prediction_model = GoalPredictionModel()

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
                        match_day = datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M:%S').date()
                    except Exception as e:
                        match_day = datetime.strptime(row['start_time'], '%d/%m/%Y %H:%M').date()

                    today = datetime.now().date()
                    if match_day < today:
                        home_team = row['home_team'].title()
                        away_team = row['away_team'].title()
                        prediction = row['prediction']

                        host_score, guest_score = self.match_results(home_team, away_team, match_day)
                        if host_score is not None and guest_score is not None:
                            total_score = int(host_score) + int(guest_score)

                            if '15' in prediction and total_score > 1:
                                row['status'] = 'WON'
                            elif '25' in prediction and total_score > 2:
                                row['status'] = 'WON'
                            elif 'GG' in prediction and int(host_score) > 0 and int(guest_score) > 0:
                                row['status'] = 'WON'
                            else:
                                row['status'] = 'LOST'

                        else:
                            row['status'] = '--'

                        print(f'{match_day} {home_team} vs {away_team} : {host_score} - {guest_score} : {prediction} : {row["status"]}')

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

    def __call__(self):
        """
        class entry point
        """
        print(f'Execution started at {datetime.now()}')

        start_date = self.last_inserted_date()
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        for market in self.markets:
            self.load_date(start_date, end_date, market)

        self.update_match_status()

        self.fetch_upcoming(self.sport_id)

        self.predict_upcoming_matches()
        
        print(f'Execution completed at {datetime.now()}')

Main()()
