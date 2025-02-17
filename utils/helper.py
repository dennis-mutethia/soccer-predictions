
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
            match.home_results = open_match[6] 
            match.status = open_match[7] 
            match.away_results = open_match[8] 
            match.overall_prob = int(open_match[9])    
            matches.append(match)
            if match.status is not None:
                played += 1
                won += 0 if match.status == 'LOST' else 1
                
        return matches, played, won
    