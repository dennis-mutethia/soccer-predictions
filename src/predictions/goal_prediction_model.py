import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from prep.filters import Filters

class GoalPredictionModel:
    def __init__(self):
        self.features = ['host_score', 'guest_score']
        self.model = LogisticRegression()

    def train_model(self, X_train, y_train):
        #print(f"Training model...")
        self.model.fit(X_train, y_train)

    def evaluate_model(self, X_test, y_test):
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        #print(f"Model Accuracy: {round(accuracy*100)}%")

    def predict_for_future_matches(self, future_matches):
        predictions = self.model.predict(future_matches[self.features])
        return predictions

    def __call__(self, csv_filename, home_team, away_team, target):        
        filters = Filters(csv_filename)

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
        sum_true_team_1 = future_predictions_team_1.sum()
        sum_true_team_2 = future_predictions_team_2.sum()

        # Calculate the count of False
        count_false_team_1 = len(future_predictions_team_1) - sum_true_team_1
        count_false_team_2 = len(future_predictions_team_2) - sum_true_team_2
        
        is_true = sum_true_team_1+sum_true_team_2
        is_false = count_false_team_1+count_false_team_2

        print(f"""
            {home_team} vs {away_team}
            Prediction: {target}
            True: {round(is_true*100/(is_true+is_false))}%
            False: {round(is_false*100/(is_true+is_false))}%
        """)
