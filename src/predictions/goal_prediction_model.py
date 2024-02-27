import csv, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from prep.filters import Filters

class GoalPredictionModel:
    def __init__(self):
        self.csv_predictions = './data/predictions.csv' 
        self.features = ['host_score', 'guest_score']
        self.model = LogisticRegression()
        self.inserted_matches = set()
        self.read_existing_matches()

    def train_model(self, X_train, y_train):
        try:
            self.model.fit(X_train, y_train)
        except Exception as e:
            print(f"An error occurred in train_model: {e}")

    def evaluate_model(self, X_test, y_test):
        try:
            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
        except Exception as e:
            print(f"An error occurred in evaluate_model: {e}")

    def predict_for_future_matches(self, future_matches):
        try:
            predictions = self.model.predict(future_matches[self.features])
            return predictions
        except Exception as e:
            print(f"An error occurred in predict_for_future_matches: {e}")
            return None

    def __call__(self, csv_match_data, start_time, home_team, away_team, target, min_probability):
        try:
            filters = Filters(csv_match_data)

            team_1_matches = filters.filter_matches_by_team(home_team)
            team_2_matches = filters.filter_matches_by_team(away_team)

            # Create instances of the GoalPredictionModel class  prediction
            model_team_1 = model_team_2 = GoalPredictionModel()

            # Train models
            model_team_1.train_model(team_1_matches[self.features], team_1_matches[target])
            model_team_2.train_model(team_2_matches[self.features], team_2_matches[target])

            # Evaluate models if needed
            model_team_1.evaluate_model(team_1_matches[self.features], team_1_matches[target])
            model_team_2.evaluate_model(team_2_matches[self.features], team_2_matches[target])

            # Predict for future matches
            future_predictions_team_1 = model_team_1.predict_for_future_matches(team_1_matches)
            future_predictions_team_2 = model_team_2.predict_for_future_matches(team_2_matches)

            # Assuming future_predictions_team_1 and future_predictions_team_2 are the prediction arrays
            if future_predictions_team_1 is not None and future_predictions_team_2 is not None:
                sum_true_team_1 = future_predictions_team_1.sum()
                sum_true_team_2 = future_predictions_team_2.sum()

                # Calculate the count of False
                count_false_team_1 = len(future_predictions_team_1) - sum_true_team_1
                count_false_team_2 = len(future_predictions_team_2) - sum_true_team_2
                
                is_true = sum_true_team_1 + sum_true_team_2
                is_false = count_false_team_1 + count_false_team_2

                perc_true = round(is_true * 100 / (is_true + is_false))
                perc_fail = round(is_false * 100 / (is_true + is_false))

                if perc_true >= min_probability:
                    print(f'{start_time} {home_team} vs {away_team} = {target.upper()} - {perc_true}%')
                    self.append_to_csv(start_time, home_team, away_team, target.upper(), perc_true)
                    
                if perc_true >= min_probability+10 and '1' in target :
                    print(f"{start_time} {home_team} vs {away_team} = {target.replace('1', '2').upper()} - {perc_true-10}%")
                    self.append_to_csv(start_time, home_team, away_team, target.replace('1', '2').upper(), perc_true-10)

                elif perc_fail >= min_probability:
                    target = target.replace('gg', 'ng').replace('ov', 'un')
                    print(f'{start_time} {home_team} vs {away_team} = {target.upper()} - {perc_fail}%')

        except Exception as e:
            print(f"An error occurred in __call__: {e}")
            # Handle the error or just continue to the next iteration
            # handle_error(e)  # You may want to define a function to handle the error


    def read_existing_matches(self):
        try:
            with open(self.csv_predictions, mode='r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    match_identifier = (row['start_time'], row['home_team'], row['away_team'], row['prediction'], row['probability'])
                    self.inserted_matches.add(match_identifier)
        except FileNotFoundError:
            print(f"An error occurred in read_existing_matches: {e}")

    def append_to_csv(self, start_time, home_team, away_team, prediction, probability):
        try:
            with open(self.csv_predictions, mode='a', newline='') as csv_file:
                fieldnames = ['start_time', 'home_team', 'away_team', 'prediction', 'probability']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                # Check if the file is empty, if so write the header
                if csv_file.tell() == 0:
                    writer.writeheader()

                match_identifier = (start_time, home_team, away_team, prediction, f'{probability}')
                
                if match_identifier not in self.inserted_matches:
                    writer.writerow({
                        'start_time': start_time,
                        'home_team': home_team,
                        'away_team': away_team,
                        'prediction': prediction,
                        'probability': probability
                    })

                    # Add the match identifier to the set
                    self.inserted_matches.add(match_identifier)
        except FileNotFoundError:
            print(f"An error occurred in append_to_csv: {e}")