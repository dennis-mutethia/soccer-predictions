import requests, csv, pandas
from upcoming_match import UpcomingMatch

class FetchUpcoming:
    def __init__(self, csv_filename):
        self.csv_filename = csv_filename
        self.inserted_matches = set()
        self.read_existing_matches()

    def read_existing_matches(self):
        try:
            with open(self.csv_filename, mode='r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    match_identifier = (row['start_time'], row['home_team'], row['away_team'])
                    self.inserted_matches.add(match_identifier)
        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            pass

    def fetch_data(self, url):
        headers = {
            'User-Agent': 'PostmanRuntime/7.36.3',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data:
                matches_data = json_data['data']
                matches_objects = [UpcomingMatch(match) for match in matches_data]
                return matches_objects
            else:
                print("Invalid JSON data format")
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")

    def append_to_csv(self, matches, csv_filename):
        with open(csv_filename, mode='a', newline='') as csv_file:
            fieldnames = ['start_time', 'home_team', 'away_team']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Check if the file is empty, if so write the header
            if csv_file.tell() == 0:
                writer.writeheader()

            for match in matches:
                match_identifier = (match.start_time, match.home_team, match.away_team)
                
                if match_identifier not in self.inserted_matches:
                    writer.writerow({
                        'start_time': match.start_time,
                        'home_team': match.home_team,
                        'away_team': match.away_team
                    })

                    # Add the match identifier to the set
                    self.inserted_matches.add(match_identifier)
                    print(f'New Match Added')
                else:
                    print(f'Match Already exists - Skipped')

    def __call__(self, sport_id='14'):
        url = f"https://api.betika.com/v1/uo/matches?limit=100&tab=2&sub_type_id=162&sport_id={sport_id}&sort_id=2&period_id=-1&esports=false&is_srl=false&page=1"
        matches = self.fetch_data(url)

        if matches:
            self.append_to_csv(matches, self.csv_filename)
            print(f"Data for sport_id: {sport_id} appended to {self.csv_filename}")
        else:
            print(f"No data fetched for sport_id : {sport_id}")
