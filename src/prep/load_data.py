import requests, csv, pandas
from match_day import MatchData


class LoadData:
    def __init__(self, csv_filename):
        self.csv_filename = csv_filename
        self.inserted_matches = set()
        self.read_existing_matches()

    def read_existing_matches(self):
        try:
            with open(self.csv_filename, mode='r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    match_identifier = (row['match_day'], row['host_name'], row['guest_name'])
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
            if json_data and isinstance(json_data, list) and json_data[0]:
                matches_data = json_data[0]
                matches_objects = [MatchData(match) for match in matches_data]
                return matches_objects
            else:
                print("Invalid JSON data format")
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")

    def append_to_csv(self, matches, csv_filename):
        with open(csv_filename, mode='a', newline='') as csv_file:
            fieldnames = ['match_day', 'host_name', 'guest_name', 'host_score', 'guest_score', 'ov15', 'ov25', 'gg']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Check if the file is empty, if so write the header
            if csv_file.tell() == 0:
                writer.writeheader()

            for match in matches:
                match_identifier = (match.date, match.host_name, match.guest_name)
                
                if match_identifier not in self.inserted_matches:
                    if match.host_score is not None and match.guest_score is not None:
                        ov15 = int(match.host_score) + int(match.guest_score) > 1
                        ov25 = int(match.host_score) + int(match.guest_score) > 2
                        gg = int(match.host_score) > 0 and int(match.guest_score) > 0

                        writer.writerow({
                            'match_day': match.date,
                            'host_name': match.host_name,
                            'guest_name': match.guest_name,
                            'host_score': match.host_score,
                            'guest_score': match.guest_score,
                            'ov15': ov15,
                            'ov25': ov25,
                            'gg': gg
                        })

                        # Add the match identifier to the set
                        self.inserted_matches.add(match_identifier)
                        print(f'New Match Added')
                else:
                    print(f'Match Already exists - Skipped')

    def __call__(self, start_date, end_date, market='1x2'):
        date_range = pandas.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d')

        for date in date_range:
            url = f"https://forebet.com/scripts/getrs.php?ln=en&tp={market}&in={date}&ord=0&tz=+180&tzs=0&tze=0"
            matches = self.fetch_data(url)

            if matches:
                self.append_to_csv(matches, self.csv_filename)
                print(f"Data for {date} appended to {self.csv_filename}")
            else:
                print(f"No data fetched for {date}")
