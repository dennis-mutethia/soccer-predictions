import csv
import pandas as pd
from datetime import datetime, timedelta
from prep.load_data import LoadData
from prep.fetch_upcoming import FetchUpcoming
from predictions.goal_prediction_model import GoalPredictionModel

class Main:
    def __init__(self):
        self.csv_match_data = './data/match_data.csv' 
        self.csv_upcoming_matches = './data/upcoming_matches.csv' 
        self.markets = ['1x2','uo','bts'] 
        self.targets = ['gg', 'ov15', 'ov25']
        self.min_probability = 75

        self.load_date = LoadData(self.csv_match_data)
        self.fetch_upcoming = FetchUpcoming(self.csv_upcoming_matches)
        self.goal_prediction_model = GoalPredictionModel()

    def team_exists_in_match_data(self, team):
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
        try:
            with open(self.csv_upcoming_matches, mode='r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    start_time = row['start_time']
                    home_team = row['home_team'].title()
                    away_team = row['away_team'].title()
                    if self.team_exists_in_match_data(home_team) and self.team_exists_in_match_data(away_team):
                        for target in self.targets:
                            try:
                                self.goal_prediction_model(self.csv_match_data, start_time, home_team, away_team, target, self.min_probability)
                            except ValueError as e:
                                print(f"An error occurred: {e}")
                                # Continue with the next iteration of the loop
                                continue

        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            pass
        
    def last_inserted_date(self):
        # Read the CSV file and get the last row
        with open(self.csv_match_data, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            last_row = rows[-1]

        # Extract the match_day value from the last row
        return last_row[0]

    def __call__(self):         
        start_date = self.last_inserted_date()
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        markets = ['1x2']  
        sport_id='14'
 
        for market in self.markets:  
            self.load_date(start_date, end_date, market)

        self.fetch_upcoming(sport_id)
        
        self.predict_upcoming_matches()
    
try:
    Main()()
except Exception as e:
    print(e)
