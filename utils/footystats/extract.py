import pytz, tzlocal, re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from unidecode import unidecode

class Extract:    
    def __init__(self):
        self.base_url = 'https://footystats.org/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            }
        self.predicted_matches = []

    def fetch_results(self, match_url, kickoff):
        home_results = None 
        away_results = None
        live = False
        
        try:
            # Send the request with headers
            response = requests.get(match_url, headers=self.headers)

            # Check if the request was successful
            if response.status_code == 200:
                html_content = response.text

                # Parse the HTML content
                soup = BeautifulSoup(html_content, 'html.parser')
                
                p_results = soup.find('p', class_='ac fs14e bold')
                if p_results is None:
                    p_results = soup.find('p', class_='ac fs2e bold')
                    live = True
                
                    # Extract the first <a> element with the specified class
                    a_tag = soup.find('a', class_='fixture changeH2HDataButton_neo')
                    if a_tag is not None:                    
                        start_time = a_tag.find('time', class_='timezone-convert-match-h2h-neo').text.strip()
                        start_time = datetime.strptime(start_time, "%b %d, %Y")
                        if start_time.date() == kickoff.date():
                            results = a_tag.find_all('span')
                            home_results = int(results[0].text.strip())
                            away_results = int(results[1].text.strip())
                            live = False  
                
                if p_results is not None:
                    parts = p_results.text.strip().split(" - ")

                    # Convert the split parts to integers
                    home_results = int(parts[0])
                    away_results = int(parts[1])
                     
        except Exception as e:
            pass
        
        return home_results, away_results, live
    
    def fetch_matches(self, endpoint):     
        url = self.base_url + endpoint
        matches = []

        # Send the request with headers
        response = requests.get(url, headers=self.headers)

        # Check if the request was successful
        if response.status_code == 200:
            html_content = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extracting data
            match_divs = soup.find_all('div', class_='betWrapper')
            for match_div in match_divs:                
                try:
                    odds = float(match_div.find('div', class_='odds').text.strip().replace('Odds',''))
                    match_data = [data_elem.text.strip() for data_elem in match_div.find_all('div', class_='data')]
                    stat_data = [data_elem.text.strip() for data_elem in match_div.find_all('div', class_='statData')]
                    over_0_5_home_perc = over_1_5_home_perc = over_2_5_home_perc = over_3_5_home_perc = 0
                    over_0_5_away_perc = over_1_5_away_perc = over_2_5_away_perc = over_3_5_away_perc = 0

                    teams = match_data[0].split(' vs ')
                    
                    hrefs = [url_elem for url_elem in match_div.find_all('a')]
                    for href in hrefs:
                        if href.text.strip() == 'View H2H Stats':
                            match_url = 'https://footystats.org' + href['href']
                            
                            # Send the request with headers
                            response_2 = requests.get(match_url, headers=self.headers)

                            # Check if the request was successful
                            if response_2.status_code == 200:
                                html_content_2 = response_2.text

                                # Parse the HTML content
                                soup_2 = BeautifulSoup(html_content_2, 'html.parser')
                                
                                #h2h-trailing-text w90 cf m0Auto
                                analysis = soup_2.find('p', class_='h2h-trailing-text w90 cf m0Auto').text.strip()
                                
                                stats = soup_2.find_all('div', class_='lh14e stat-human')
                                home_analysis = stats[0].text.strip()
                                away_analysis = stats[1].text.strip()
                                for stat in stats:
                                    #print(stat)
                                    analysis = analysis + '<br />' +stat.text.strip()
                                    
                                # Find the div with id "over-prefix-0"
                                over_prefix_div = soup_2.find('div', id='over-prefix-0')
                                
                                # Extract the data rows
                                data_rows = over_prefix_div.find_all('tr', class_='row')

                                # Iterate over each row to extract the data
                                for row in data_rows:
                                    columns = row.find_all('td')
                                    if columns:
                                        goal_type = columns[0].text.strip()
                                        home_team_percentage = columns[1].text.strip().replace('%', '')
                                        away_team_percentage = columns[2].text.strip().replace('%', '')     
                                        
                                        if '0.5' in goal_type:
                                            over_0_5_home_perc = int(home_team_percentage) 
                                            over_0_5_away_perc = int(away_team_percentage) 
                                            
                                        elif '1.5' in goal_type:
                                            over_1_5_home_perc = int(home_team_percentage) 
                                            over_1_5_away_perc = int(away_team_percentage)  
                                            
                                        elif '3.5' in goal_type:
                                            over_2_5_home_perc = int(home_team_percentage) 
                                            over_2_5_away_perc = int(away_team_percentage)  
                                            
                                        elif '2.5' in goal_type:
                                            over_3_5_home_perc = int(home_team_percentage) 
                                            over_3_5_away_perc = int(away_team_percentage) 
            
                                        
                    # Remove ordinal suffixes (st, nd, rd, th) using regex
                    date_str_modified = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', match_data[1])

                    # Define the format without ordinal suffix
                    date_format = '%d %B at %I:%M%p'

                    # Parse the modified date string
                    parsed_date = datetime.strptime(date_str_modified, date_format)

                    start_time = parsed_date.replace(year=datetime.now().year).strftime("%d-%m-%Y %H:%M:%S")

                    home_perc = float(stat_data[0].replace('%',''))
                    away_perc = float(stat_data[1].replace('%',''))

                    points_per_game_home = float(stat_data[2])
                    points_per_game_away = float(stat_data[3])

                    average_goals_home = float(stat_data[4])
                    average_goals_away = float(stat_data[5])  

                    match = {
                        "home_team" : unidecode(teams[0]),
                        "away_team" : unidecode(teams[1]),
                        "prediction" : None,
                        "odd" : odds,
                        "start_time" : start_time,
                        "home_perc" : home_perc,
                        "away_perc" : away_perc,
                        "meetings": re.search(r'(\d+)\s+meetings', analysis).group(1),
                        "points_per_game_home" : points_per_game_home,
                        "points_per_game_away" : points_per_game_away,
                        "average_goals_home" : average_goals_home,
                        "average_goals_away" : average_goals_away,
                        "match_url": match_url,
                        "over_0_5_home_perc": over_0_5_home_perc,
                        "over_0_5_away_perc": over_0_5_away_perc,
                        "over_1_5_home_perc": over_1_5_home_perc,
                        "over_1_5_away_perc": over_1_5_away_perc,
                        "over_2_5_home_perc": over_2_5_home_perc,
                        "over_2_5_away_perc": over_2_5_away_perc,
                        "over_3_5_home_perc": over_3_5_home_perc,
                        "over_3_5_away_perc": over_3_5_away_perc,
                        "home_results": None,
                        "away_results": None,
                        "analysis": unidecode(analysis),
                        "home_analysis" : home_analysis,
                        "away_analysis" : away_analysis
                    }
                                        
                    if datetime.now().strftime('%Y-%m-%d') == datetime.strptime(start_time, ("%d-%m-%Y %H:%M:%S")).strftime('%Y-%m-%d'):
                        matches.append(match)

                except Exception as e:
                    #print(e)
                    pass

        else:
            pass
            #print("Failed to retrieve the page. Status code:", response.status_code)

        return matches
 
    def predict_overs(self, match):
        prediction = None
        overall_prob = 0  
        
        if (match["over_3_5_home_perc"] >= 90) or (match["over_3_5_away_perc"] >= 90):
            prediction = 'TOTAL OVER 3.5'
            overall_prob = (match["over_3_5_home_perc"] + match["over_3_5_away_perc"])/2        
        
        elif (match["over_2_5_home_perc"] >= 90) or (match["over_2_5_away_perc"] >= 90):
            prediction = 'TOTAL OVER 2.5'
            overall_prob = (match["over_2_5_home_perc"] + match["over_2_5_away_perc"])/2     
            
        elif match["over_1_5_home_perc"] >= 90 and match["over_1_5_away_perc"] >= 90:
            prediction = 'TOTAL OVER 2.5'
            overall_prob = (match["over_1_5_home_perc"] + match["over_1_5_away_perc"])/2     
            
        elif match["over_1_5_home_perc"] > 80 and match["over_1_5_away_perc"] > 80:
            prediction = 'BOTH TEAMS TO SCORE'
            overall_prob = (match["over_0_5_home_perc"] + match["over_0_5_away_perc"])/2        
            
        elif match["home_perc"] >= 80 and match["over_1_5_home_perc"] > 80:
            prediction = 'HOME WIN'
            overall_prob = match["home_perc"] 
        
        elif match["away_perc"] >= 80 and match["over_1_5_away_perc"] > 80:
            prediction = 'AWAY WIN'
            overall_prob = match["away_perc"]           
        
        elif (match["over_1_5_home_perc"] >= 90) or (match["over_1_5_away_perc"] >= 90):
            prediction = 'TOTAL OVER 1.5'
            overall_prob = (match["over_1_5_home_perc"] + match["over_1_5_away_perc"])/2    
        
        elif match["over_0_5_home_perc"] >= 90:
            prediction = 'HOME TOTAL OVER 0.5'  
            overall_prob = match["over_0_5_home_perc"]
        
        elif match["over_0_5_away_perc"] >= 90:
            prediction = 'AWAY TOTAL OVER 0.5'  
            overall_prob = match["over_0_5_away_perc"]
        
        print(f'{match["start_time"]} {match["home_team"]} vs {match["away_team"]} - {prediction}')
        
        return prediction, overall_prob
       
    def predict(self, matches):
        team_names = []
        for match in matches:
            if int(match["meetings"]) >=5:
                teams = f'{match["home_team"]} vs {match["away_team"]}'
                prediction, overall_prob = self.predict_overs(match) # self.predict_over(match)
                
                if teams not in team_names and prediction is not None:
                    team_names.append(teams)
                    match["prediction"] = prediction
                    match["overall_prob"] = overall_prob
                    self.predicted_matches.append(match)

    def get_start_time(self, match):
        return match["start_time"]

    def get_local_timezone(self):
        try:
            return tzlocal.get_localzone()
        except Exception as e:
            return pytz.timezone('Africa/Nairobi') 
            
    def __call__(self):   
        to_return = [] 
        matches = self.fetch_matches('predictions')   
        matches_home_wins = self.fetch_matches('predictions/home-wins')    
        matches_away_wins = self.fetch_matches('predictions/away-wins')    
        matches_1x2 = self.fetch_matches('predictions/1x2')     
        matches_btts = self.fetch_matches('predictions/btts') 
        matches_over_15 = self.fetch_matches('predictions/over-15-goals') 
        matches_over_25 = self.fetch_matches('predictions/over-25-goals')
        matches_tomorrow = self.fetch_matches('predictions/tomorrow')    
        
        matches = matches + matches_home_wins + matches_away_wins + matches_1x2 + matches_btts + matches_over_15 + matches_over_25 + matches_tomorrow
                       
        self.predict(matches)
        sorted_matches = sorted(self.predicted_matches, key=self.get_start_time)

        for match in sorted_matches:
            # Parse the start_time string into a naive datetime object
            start_time_dt = datetime.strptime(match["start_time"], '%d-%m-%Y %H:%M:%S')
            
            start_time_local = start_time_dt.astimezone(self.get_local_timezone())

            match["start_time"] = start_time_dt #start_time_local.replace(tzinfo=None) #utc_time.astimezone(eat_tz).astimezone(eat_tz)
                                             
            to_return.append(match)
                        
        return to_return
