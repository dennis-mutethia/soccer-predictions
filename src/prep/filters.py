import pandas as pd

class Filters:
    def __init__(self, csv_filename):
        self.csv_filename = csv_filename
        self.match_data = pd.read_csv(self.csv_filename)

    def filter_matches_by_team(self, team_name):
        """
        Filter matches played by a particular team, either as a host or guest.
        
        Parameters:
        - data (DataFrame): DataFrame containing match data.
        - team_name (str): Name of the team to filter matches for.

        Returns:
        - DataFrame: Filtered DataFrame containing matches played by the specified team.
        """
        filtered_data = self.match_data[(self.match_data['host_name'] == team_name) | (self.match_data['guest_name'] == team_name)]
        return filtered_data

    
