

from utils.jackpots.betika import Betika
from utils.jackpots.shabiki import Shabiki
from utils.jackpots.sportpesa import Sportpesa
from utils.postgres_crud import PostgresCRUD


class Jackpots():
    def __init__(self):
        self.shabiki = Shabiki()
        self.betika = Betika()
        self.sportpesa = Sportpesa()
        self.postgres_crud = PostgresCRUD()

    def predict(self):        
        # Step 1: Fetch odds data from the database
        odds_df = self.postgres_crud.fetch_all_odds()

        # Step 2: Group by event_id and calculate changes for each event
        odds_df['home_change'] = odds_df.groupby(['id', 'event_id'])['home_odds'].diff()
        odds_df['draw_change'] = odds_df.groupby(['id', 'event_id'])['draw_odds'].diff()
        odds_df['away_change'] = odds_df.groupby(['id', 'event_id'])['away_odds'].diff()

        # Fill NaN values with 0 (for the first row in each group)
        odds_df.fillna(0, inplace=True)
        
        # Step 3: Apply the prediction logic for each (id, event_id) group
        overall_predictions = odds_df.groupby(['id', 'event_id']).apply(self.predict_outcome_per_event)

        # Step 4: Update the original DataFrame with overall predictions
        # Reset index of overall_predictions to allow merging back into odds_df
        overall_predictions = overall_predictions.reset_index(level=['id', 'event_id'])

        # Join the predictions back to the original odds_df
        odds_df = odds_df.merge(overall_predictions[['id', 'event_id', 0]], on=['id', 'event_id'], how='left')

        # Rename the prediction column (0) to 'prediction'
        odds_df.rename(columns={0: 'prediction'}, inplace=True)

        # Step 5: Display predictions for debugging
        print(odds_df)

        # Step 6: Update predictions in the database
        self.postgres_crud.update_prediction_to_jackpot_selections(odds_df)

        
    # Step 3: Define the prediction logic per event
    def predict_outcome_per_event(self, group):
        total_home_change = group['home_change'].sum()
        total_draw_change = group['draw_change'].sum()
        total_away_change = group['away_change'].sum()

        # Prediction based on odds trends
        if total_home_change < 0 and total_away_change > 0 and total_draw_change >= 0:
            return "Home Win"
        elif total_away_change < 0 and total_home_change > 0 and total_draw_change >= 0:
            return "Away Win"
        elif total_draw_change < 0 and total_home_change >= 0 and total_away_change >= 0:
            return "Draw"
        else:
            return "No Clear Prediction"
        
    def __call__(self):
        #jackpots_shabiki = self.shabiki.get_jackpot_selections()
        bkj = self.betika.get_jackpot_selections()
        spj = self.sportpesa.get_jackpot_selections()
        
        jackpots = bkj + spj
        self.postgres_crud.add_jackpot_selections(jackpots)
            
            
if __name__ == '__main__':
    jackpots = Jackpots()
    jackpots()
    jackpots.predict()
    