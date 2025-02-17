
import json
import requests
from utils.betika import Betika
from utils.entities import Match
from utils.postgres_crud import PostgresCRUD

class Helper():   
    def __init__(self):
        pass

    def fetch_data(self, url, timeout=10):
        """
        Fetch data from the given URL.

        Args:
            url (str): The URL to fetch data from.
            timeout (int, optional): The timeout for the HTTP request.

        Returns:
            dict or None: The JSON data if successful, otherwise None.
        """
        headers = {
            'User-Agent': 'PostmanRuntime/7.36.3',
        }

        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            json_data = response.json()
            if json_data:
                return json_data
            print("Invalid JSON data format")
        else:
            print(f"{response}")

        return None
    
    def post_data(self, url, body, timeout=10):
        """
        Fetch data from the given URL with POST method.

        Args:
            url (str): The URL to fetch data from.
            body (dict): The body of the POST request.
            timeout (int, optional): The timeout for the HTTP request.

        Returns:
            dict or None: The JSON data if successful, otherwise None.
        """

        body_dict = json.loads(body)

        response = requests.post(url, json=body_dict, timeout=timeout)
        return response.json()


    def get_background_color(self, perc):
        color_map = [
            (100, 'green'),
            (90, 'limegreen'),
            (80, 'lime'),
            (70, 'lawngreen'),
            (60, 'yellow'),
            (50, 'orange'),
            (40, 'darkorange'),
            (30, 'tomato'),
            (20, 'orangered')
        ]

        for threshold, color in color_map:
            if perc >= threshold:
                return color
        return 'red'

    def highlight_analysis(self, analysis):
        if analysis:
            analysis = analysis.replace("a Very Low Chance", 'a <span style="background-color: red border-radius: 5px">Very Low Chance</span>')
            analysis = analysis.replace("a Low Chance", 'a <span style="background-color: tomato border-radius: 5px">Low Chance</span>')
            analysis = analysis.replace("Uncertainty", '<span style="background-color: yellow border-radius: 5px">Uncertainty</span>')
            analysis = analysis.replace("Medium Chance", '<span style="background-color: lawngreen border-radius: 5px">Medium Chance</span>')
            analysis = analysis.replace("a High Chance", 'a <span style="background-color: lime border-radius: 5px">High Chance</span>')  
            analysis = analysis.replace("a Very High Chance", 'a <span style="background-color: green border-radius: 5px">Very High Chance</span>')
        return analysis

    def fetch_matches(self, day, comparator='=', status="AND status IS NOT NULL"):
        matches = []
        played = 0
        won = 0
        for open_match in PostgresCRUD().fetch_matches(day, comparator, status):
            match = Match()
            match.kickoff = open_match[1]
            match.home_team = open_match[2]
            match.away_team = open_match[3]
            match.prediction = open_match[4]    
            match.odd = open_match[5]    
            # match.over_0_5_home_perc = int(open_match[9])
            # match.over_0_5_away_perc = int(open_match[10]) 
            # match.over_1_5_home_perc = int(open_match[11])
            # match.over_1_5_away_perc = int(open_match[12])
            # match.over_2_5_home_perc = int(open_match[13]) 
            # match.over_2_5_away_perc = int(open_match[14])
            # match.over_3_5_home_perc = int(open_match[15]) 
            # match.over_3_5_away_perc = int(open_match[16])
            match.home_results = open_match[17] 
            match.status = open_match[18] 
            match.away_results = open_match[19] 
            match.overall_prob = int(open_match[21])    
            #match.analysis = open_match[22]
            matches.append(match)
            if match.status is not None:
                played += 1
                won += 0 if match.status == 'LOST' else 1
                
        return matches, played, won
    