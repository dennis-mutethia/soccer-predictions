import csv
import pandas as pd
from datetime import datetime
from prep.load_data import LoadData
from prep.fetch_upcoming import FetchUpcoming
from predictions.goal_prediction_model import GoalPredictionModel

class Main:
    def __init__(self):
        self.csv_match_data = './data/match_data.csv' 
        self.csv_upcoming_matches = './data/upcoming_matches.csv' 
        self.targets = ['gg', 'ov15', 'ov25']


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
                    start_time_str = row['start_time']
                    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                    if start_time > datetime.now():
                        home_team = row['home_team'].title()
                        away_team = row['away_team'].title()
                        if self.team_exists_in_match_data(home_team) and self.team_exists_in_match_data(away_team):
                            for target in self.targets:
                                self.goal_prediction_model(self.csv_match_data, start_time_str, home_team, away_team, target)
        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            pass
        

    def __call__(self): 
        
        start_date = '2021-01-01'
        end_date = '2021-01-10' 
        markets = ['1x2']  
        sport_id='14'

        self.fetch_upcoming(sport_id)

        #markets = ['1x2','uo','bts']  
        #for market in markets:    
        #    self.load_date(start_date, end_date, market)

        self.predict_upcoming_matches()
    
try:
    Main()()
except Exception as e:
    print(e)
