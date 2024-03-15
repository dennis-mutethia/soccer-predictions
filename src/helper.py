import json, requests

class Helper:
    """
    This class provides helper methods for fetching data.
    """

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


