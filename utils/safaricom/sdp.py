
import os, time
from dotenv import load_dotenv

from .request import Request
from .exceptions.sdp_exception import SDPException


class SDP:
    """
    Main application class for Safaricom SDP integration.
    """

    def __init__(self, debug_level=None):
        """
        SDP constructor.

        :param api_username: API username for the CP from SDP account
        :param api_password: API password for the CP from SDP account
        :param cp_id: Identifier for the CP
        :param debug_level: Debug level for the app
        """
        load_dotenv()
        
        self.api_username = os.getenv('API_USERNAME')
        self.api_password = os.getenv('API_PASSWORD')
        self.cp_id = os.getenv('CP_ID')

        self.sandbox_base_url = os.getenv('SANDBOX_BASE_URL')
        self.live_base_url = os.getenv('SDP_BASE_URL')
        
        self.debug_level = debug_level

        # Default to sandbox environment
        self.base_url = self.sandbox_base_url

        self.link_id = None
        self.cp_username = None
        self.token = None
        self.request = None

    def use_live(self):
        """
        Switch to using the live environment.
        :return: self
        """
        self.base_url = self.live_base_url
        return self

    def use_sandbox(self):
        """
        Switch to using the sandbox environment.
        :return: self
        """
        self.base_url = self.sandbox_base_url
        return self

    def init(self):
        """
        Initialize the app by setting the token.

        :return: self
        :raises SDPException: If token generation fails
        """
        self.request = Request(self.base_url)
        self.token = self.generate_token(self.api_username, self.api_password)
        self.request.response_body = None  # Reset the response body

    def generate_token(self, username, password):
        """
        Generate a token using provided username and password.

        :param username: API username
        :param password: API password
        :return: Token string
        :raises SDPException: If token generation fails
        """
        body = {
            'username': username,
            'password': password
        }

        response = self.request.request("POST", "auth/login", None, body) # type: ignore

        if not response.success:
            raise SDPException(response.error_message, response.error_code)

        token = response.response_body.get('token', "")
        return token

    @staticmethod
    def generate_timestamp():
        """
        Generate a timestamp in the format YYYYMMDDHHmmss.

        :return: Timestamp string
        """
        return time.strftime("%Y%m%d%H%M%S", time.localtime())
