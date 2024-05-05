import requests
from datetime import datetime
from bs4 import BeautifulSoup

class Extract:    
    def __init__(self):
        self.base_url = 'https://footystats.org/predictions/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }

    def fetch(self, prediction): 
        url = self.base_url + prediction
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
                    match_time = datetime.strptime(match_data[1], "%dth %B at %I:%M%p").replace(year=datetime.now().year).strftime("%d/%m/%Y %H:%M")

                    home_perc = float(stat_data[0].replace('%',''))
                    away_perc = float(stat_data[1].replace('%',''))

                    goals_scored_home = float(stat_data[2])
                    goals_scored_away = float(stat_data[3])
                    goals_conceded_home = float(stat_data[4])
                    goals_conceded_away = float(stat_data[5])

                    if home_perc > 65 and away_perc > 65:
                        if (goals_scored_home>1 or goals_scored_away>1) and (goals_conceded_home>1 or goals_conceded_away>1):
                            #print(f'{match_time} - {teams} {home_perc}:{away_perc} {goals_scored_home}-{goals_scored_away} {goals_conceded_home}-{goals_conceded_away}')
                            if teams not in team_names:
                                team_names.append(teams)
                                print(f'{match_time} {teams} [{prediction.upper()}] @ {odds}')

                except Exception as e:
                    pass

        else:
            print("Failed to retrieve the page. Status code:", response.status_code)

    def __call__(self):
        self.fetch('btts')


Extract()()