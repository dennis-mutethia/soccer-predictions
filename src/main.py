import pandas as pd
from prep.load_data import LoadData
from predictions.goal_prediction_model import GoalPredictionModel

class Main:
    def __init__(self):
        self.csv_filename = './data/match_data.csv' 

        self.load_date = LoadData(self.csv_filename)
        self.goal_prediction_model = GoalPredictionModel()

    def __call__(self): 
        start_date = '2021-01-01'
        end_date = '2024-02-25'       
        #self.load_date(start_date, end_date)

        home_team = 'Arema FC'
        away_team = 'Persija Jakarta'
        targets = ['gg', 'ov15', 'ov25']

        for target in targets:
            self.goal_prediction_model(self.csv_filename, home_team, away_team, target)
try:
    Main()()
except Exception as e:
    print(e)
