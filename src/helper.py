import requests

class Helper:

    def fetch_data(self, url):
        headers = {
            'User-Agent': 'PostmanRuntime/7.36.3',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data:
                return json_data
            else:
                print("Invalid JSON data format")
        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")

        return None