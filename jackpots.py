

from utils.jackpots.betika import Betika
from utils.jackpots.shabiki import Shabiki
from utils.postgres_crud import PostgresCRUD


class Jackpots():
    def __init__(self):
        self.shabiki = Shabiki()
        self.betika = Betika()
        self.postgres_crud = PostgresCRUD()

    def predict(self):        
        odds_df = self.postgres_crud.fetch_all_odds()
        
        # Step 2: Group by event_id and calculate changes for each event
        odds_df['home_change'] = odds_df.groupby('event_id')['home_odds'].diff()
        odds_df['draw_change'] = odds_df.groupby('event_id')['draw_odds'].diff()
        odds_df['away_change'] = odds_df.groupby('event_id')['away_odds'].diff()

        # Fill NaN values with 0 (for the first row in each group)
        odds_df.fillna(0, inplace=True)
        
        # Apply the prediction logic for each event_id group
        overall_predictions = odds_df.groupby('event_id').apply(self.predict_outcome_per_event)
        
        # Step 4: Update the original DataFrame with overall predictions
        odds_df['prediction'] = odds_df['event_id'].map(overall_predictions)

        # Display predictions
        print(odds_df)
        
        #update predictions
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
            return "---"
         
    def __call__(self):
        #jackpots_shabiki = self.shabiki.get_jackpot_selections()
        jackpots = self.betika.get_jackpot_selections()
        
        self.postgres_crud.add_jackpot_selections(jackpots)
        
        
if __name__ == '__main__':
    jackpots = Jackpots()
    jackpots()
    jackpots.predict()
    