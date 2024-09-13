
import requests
from requests.exceptions import RequestException


class Request:
    def __init__(self, base_uri):
        """
        Request constructor.
        
        :param base_uri: Base URI for the HTTP client
        """
        self.client = requests.Session()
        self.base_uri = base_uri
        self.headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.success = True
        self.status_code = None
        self.status_text = None
        self.response_body = None
        self.error_code = None
        self.error_message = None
        self.debug_request_trace = None
        self.debug_response_trace = None

    def request(self, method, uri, token=None, body=None, query_params=None):
        """
        Make an HTTP request.

        :param method: HTTP method (GET, POST, etc.)
        :param uri: Endpoint URI to send the request to
        :param token: Optional token for authorization
        :param body: Optional JSON body for the request
        :param query_params: Optional query parameters for the request
        :return: self
        """
        try:
            # Add the token to headers if provided
            if token is not None:
                self.headers['X-Authorization'] = f"Bearer {token}"

            options = {
                'headers': self.headers,
                'verify': False
            }

            # Add the JSON body if provided
            if body is not None:
                options['json'] = body

            # Add query parameters if provided
            if query_params is not None:
                options['params'] = query_params

            # Perform the request
            response = self.client.request(method, f"{self.base_uri}/{uri}", **options)

            # Set response details
            self.status_code = response.status_code
            self.status_text = response.reason
            self.response_body = response.json()

        except RequestException as e:
            self.success = False
            self.debug_request_trace = str(e.request)

            # If response is available
            if e.response:
                self.status_code = e.response.status_code
                self.status_text = e.response.reason

                try:
                    self.response_body = e.response.json()
                except ValueError:
                    self.response_body = e.response.text

                self.error_code = self.response_body.get('error', "")
                self.error_message = self.response_body.get('message', "")
            else:
                # Generic error
                self.status_code = 500
                self.status_text = "Internal Server Error"
                self.error_code = e.errno if hasattr(e, 'errno') else "UNKNOWN"
                self.error_message = str(e)

        except Exception as e:
            self.success = False
            self.debug_request_trace = str(e)

            # Generic error
            self.status_code = 500
            self.status_text = "Internal Server Error"
            self.error_code = str(e.__class__.__name__)
            self.error_message = str(e)

        return self
