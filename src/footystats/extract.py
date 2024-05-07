import requests, csv
from datetime import datetime
import concurrent.futures
from bs4 import BeautifulSoup

class Extract:    
    def __init__(self):
        self.base_url = 'https://footystats.org/predictions/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }

    def predict_gg(self): 
        self.csv_predictions = './docs/predictions.csv' 
        url = self.base_url + 'btts'
        team_names = []

        # Send the request with headers
        response = requests.get(url, headers=self.headers)

        # Check if the request was successful
        if response.status_code == 200:
            html_content = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extracting data
            matches = soup.find_all('div', class_='betWrapper')

            for match in matches:
                try:
                    odds = float(match.find('div', class_='odds').text.strip().replace('Odds',''))
                    match_data = [data_elem.text.strip() for data_elem in match.find_all('div', class_='data')]
                    stat_data = [data_elem.text.strip() for data_elem in match.find_all('div', class_='statData')]

                    teams = match_data[0]
                    match_time = datetime.strptime(match_data[1], "%dth %B at %I:%M%p").replace(year=datetime.now().year).strftime("%d-%m-%Y %H:%M:%S")

                    home_perc = float(stat_data[0].replace('%',''))
                    away_perc = float(stat_data[1].replace('%',''))

                    goals_scored_home = float(stat_data[2])
                    goals_scored_away = float(stat_data[3])
                    goals_conceded_home = float(stat_data[4])
                    goals_conceded_away = float(stat_data[5])

                    if home_perc > 60 and away_perc > 60:
                        if (goals_scored_home>1 or goals_scored_away>1) and (goals_conceded_home>1 or goals_conceded_away>1):
                            #print(f'{match_time} - {teams} {home_perc}:{away_perc} {goals_scored_home}-{goals_scored_away} {goals_conceded_home}-{goals_conceded_away}')
                            if teams not in team_names:
                                team_names.append(teams)
                                print(f'{match_time} {teams} [GG] @ {odds}')
                                teams_array = teams.split(' vs ')
                                self.append_to_csv(match_time, teams_array[0], teams_array[1], 'GG', home_perc, away_perc, (home_perc+away_perc)/2)

                except Exception as e:
                    pass

        else:
            print("Failed to retrieve the page. Status code:", response.status_code)

    def predict_ov25(self): 
        self.csv_predictions = './docs/predictions.csv' 
        url = self.base_url + 'over-25-goals'
        team_names = []

        # Send the request with headers
        response = requests.get(url, headers=self.headers)

        # Check if the request was successful
        if response.status_code == 200:
            html_content = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extracting data
            matches = soup.find_all('div', class_='betWrapper')

            for match in matches:
                try:
                    odds = float(match.find('div', class_='odds').text.strip().replace('Odds',''))
                    match_data = [data_elem.text.strip() for data_elem in match.find_all('div', class_='data')]
                    stat_data = [data_elem.text.strip() for data_elem in match.find_all('div', class_='statData')]

                    teams = match_data[0]
                    match_time = datetime.strptime(match_data[1], "%dth %B at %I:%M%p").replace(year=datetime.now().year).strftime("%d-%m-%Y %H:%M:%S")

                    home_perc = float(stat_data[0].replace('%',''))
                    away_perc = float(stat_data[1].replace('%',''))

                    goals_scored_home = float(stat_data[2])
                    goals_scored_away = float(stat_data[3])
                    goals_conceded_home = float(stat_data[4])
                    goals_conceded_away = float(stat_data[5])

                    #print(f'{match_time} - {teams} {home_perc}:{away_perc} {goals_scored_home}-{goals_scored_away} {goals_conceded_home}-{goals_conceded_away}')

                    if home_perc > 60 or away_perc > 60:
                        if (goals_scored_home>=2 or goals_scored_away>=2) and (goals_conceded_home>2 or goals_conceded_away>2):
                            if teams not in team_names:
                                team_names.append(teams)
                                print(f'{match_time} {teams} [OV2.5] @ {odds}')
                                teams_array = teams.split(' vs ')
                                self.append_to_csv(match_time, teams_array[0], teams_array[1], 'OV2.5', home_perc, away_perc, (home_perc+away_perc)/2)

                except Exception as e:
                    pass

        else:
            print("Failed to retrieve the page. Status code:", response.status_code)

    def append_to_csv(self, start_time, home_team, away_team, prediction, home_prob, away_prob, overall_prob):
        try:
            with open(self.csv_predictions, mode='a', newline='') as csv_file:
                fieldnames = ['start_time', 'parent_match_id', 'home_team', 'away_team', 'prediction', 'home_prob', 'away_prob', 'overall_prob', 'status', 'odd']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                # Check if the file is empty, if so write the header
                if csv_file.tell() == 0:
                    writer.writeheader()

                writer.writerow({
                    'start_time': start_time,
                    'parent_match_id': '',
                    'home_team': home_team,
                    'away_team': away_team,
                    'prediction': prediction,
                    'home_prob': home_prob,
                    'away_prob': away_prob,
                    'overall_prob': overall_prob,
                    'status': '',
                    'odd': ''
                })

        except Exception as e:
            print(f"An error occurred in append_to_csv: {e}")

    def __call__(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            threads = []
            #create concurrency - ThreadPool for each prediction
            threads.append(executor.submit(self.predict_gg))           
            #threads.append(executor.submit(self.predict_ov25))

            # Wait for all threads to complete
            concurrent.futures.wait(threads)
