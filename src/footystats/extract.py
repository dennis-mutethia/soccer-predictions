import pytz, tzlocal, re
import requests, csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from unidecode import unidecode

class Extract:    
    def __init__(self):
        self.base_url = 'https://footystats.org/'
        self.csv_predictions = './docs/predictions.csv' 
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
    
    def predict_home_away_total(self, home_analysis, away_analysis):
        prediction = None
        if 'Very High Chance' in home_analysis and ('Very High Chance' in away_analysis or 'High Chance' in away_analysis):
            prediction = 'TOTAL OVER 2.5'
        if 'Very High Chance' in away_analysis and ('Very High Chance' in home_analysis or 'High Chance' in home_analysis):
            prediction = 'TOTAL OVER 2.5'
        if 'High Chance' in home_analysis and ('High Chance' in away_analysis or 'Moderate Chance' in away_analysis):
            prediction = 'TOTAL OVER 1.5'
        if 'High Chance' in away_analysis and ('High Chance' in home_analysis or 'Moderate Chance' in home_analysis):
            prediction = 'TOTAL OVER 1.5'
        elif 'Very High Chance' in home_analysis:
            prediction = 'HOME TOTAL OVER 1.5'
        elif 'Very High Chance' in away_analysis:
            prediction = 'AWAY TOTAL OVER 1.5'
        elif 'High Chance' in home_analysis:
            prediction = 'HOME TOTAL OVER 0.5'
        elif 'High Chance' in away_analysis:
            prediction = 'AWAY TOTAL OVER 0.5'
        
        return prediction
    
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
                        "prediction" : self.predict_home_away_total(home_analysis, away_analysis),
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
                        "analysis": unidecode(analysis)
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

    def predict_over(self, match):
        over = None
        sub_type_id = None
        overall_prob = 0
        total_possible_goals = match["average_goals_home"] + match["average_goals_away"]
                  
        if total_possible_goals >= 4.5 and (match["over_3_5_home_perc"] >= 90 or match["over_3_5_away_perc"] >= 90):
            over = 'TOTAL OVER 3.5'
            sub_type_id = 18
            overall_prob = (match["over_3_5_home_perc"] + match["over_3_5_away_perc"])/2     
                      
        elif total_possible_goals >= 3.5 and (match["over_2_5_home_perc"] >= 90 or match["over_2_5_away_perc"] >= 90):
            over = 'TOTAL OVER 2.5'
            sub_type_id = 18
            overall_prob = (match["over_2_5_home_perc"] + match["over_2_5_away_perc"])/2
        
        elif match["over_1_5_home_perc"] == 100 and match["over_1_5_away_perc"] == 100 and (match["over_2_5_home_perc"] + match["over_2_5_away_perc"])/2 > 80:
            over = 'TOTAL OVER 2.5'
            sub_type_id = 18
            overall_prob = (match["over_2_5_home_perc"] + match["over_2_5_away_perc"])/2                      
            
        elif match["over_0_5_home_perc"] == 100 and match["over_0_5_away_perc"] == 100 and (match["over_1_5_home_perc"] + match["over_1_5_away_perc"])/2 > 90:
            over = 'TOTAL OVER 1.5'
            sub_type_id = 18
            overall_prob = (match["over_1_5_home_perc"] + match["over_1_5_away_perc"])/2
        
        elif total_possible_goals >= 2.5 and (match["over_1_5_home_perc"] >= 90 or match["over_1_5_away_perc"] >= 90):
            over = 'TOTAL OVER 1.5'
            sub_type_id = 18
            overall_prob = (match["over_1_5_home_perc"] + match["over_1_5_away_perc"])/2
            
            
                      
        elif match["average_goals_home"] >= 1.5 and (match["over_0_5_home_perc"] == 100):
            over = 'HOME TOTAL OVER 0.5'  
            sub_type_id = 19    
            overall_prob = match["over_0_5_home_perc"] 
             
        elif match["average_goals_away"] >= 1.5 and match["over_0_5_away_perc"] == 100:
            over = 'AWAY TOTAL OVER 0.5'
            sub_type_id = 20
            overall_prob = match["over_0_5_away_perc"]   
            
        
        return over, sub_type_id, overall_prob
    
    def map_prediction(self, match):
        over = None
        sub_type_id = None
        overall_prob = 0   
             
        if match["prediction"] == 'TOTAL OVER 2.5':
            over = 'TOTAL OVER 2.5'
            sub_type_id = 18
            overall_prob = (match["over_2_5_home_perc"] + match["over_2_5_away_perc"])/2             
             
        elif match["prediction"] == 'TOTAL OVER 1.5':
            over = 'TOTAL OVER 1.5'
            sub_type_id = 18
            overall_prob = (match["over_1_5_home_perc"] + match["over_1_5_away_perc"])/2    
            
        if match["prediction"] == 'HOME TOTAL OVER 1.5':
            over = 'HOME TOTAL OVER 1.5'  
            sub_type_id = 19    
            overall_prob = match["over_1_5_home_perc"] 
             
        elif match["prediction"] == 'AWAY TOTAL OVER 1.5':
            over = 'AWAY TOTAL OVER 1.5'
            sub_type_id = 20
            overall_prob = match["over_1_5_away_perc"]  
               
        elif match["prediction"] == 'HOME TOTAL OVER 0.5':
            over = 'HOME TOTAL OVER 0.5'  
            sub_type_id = 19    
            overall_prob = match["over_0_5_home_perc"] 
             
        elif match["prediction"] == 'AWAY TOTAL OVER 0.5':
            over = 'AWAY TOTAL OVER 0.5'
            sub_type_id = 20
            overall_prob = match["over_0_5_away_perc"] 
            
        return over, sub_type_id, overall_prob
    
    def predict(self, matches):
        team_names = []
        for match in matches:
            if int(match["meetings"]) >=7 and 'High' in match["analysis"]:
                teams = f'{match["home_team"]} vs {match["away_team"]}'
                predictions = []
                prediction, sub_type_id, overall_prob = self.map_prediction(match) # self.predict_over(match)
                if prediction is not None:
                    predictions.append(prediction)
                
                if teams not in team_names and predictions:
                    team_names.append(teams)
                    match["prediction"] = ' & '.join(map(str, predictions))
                    match["sub_type_id"] = sub_type_id
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
        matches = self.fetch_matches('')   
        matches_1x2 = self.fetch_matches('predictions/1x2')     
        matches_btts = self.fetch_matches('predictions/btts') 
        matches_over_15 = self.fetch_matches('predictions/over-15-goals') 
        matches_over_25 = self.fetch_matches('predictions/over-25-goals')
        matches_tomorrow = self.fetch_matches('tomorrow')    
        
        matches = matches + matches_1x2 + matches_btts + matches_over_15 + matches_over_25 + matches_tomorrow
                
        self.predict(matches)
        sorted_matches = sorted(self.predicted_matches, key=self.get_start_time)

        for match in sorted_matches:
            # Parse the start_time string into a naive datetime object
            start_time_dt = datetime.strptime(match["start_time"], '%d-%m-%Y %H:%M:%S')
            
            start_time_local = start_time_dt.astimezone(self.get_local_timezone())

            match["start_time"] = start_time_local.replace(tzinfo=None) #utc_time.astimezone(eat_tz).astimezone(eat_tz)
                                             
            to_return.append(match)
                        
        return to_return
