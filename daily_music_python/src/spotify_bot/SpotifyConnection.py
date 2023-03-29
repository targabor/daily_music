import requests
import time

from typing import TYPE_CHECKING
from src.python_logger.Logger import Logger
# Place there the imports which are needed only for type checking
if TYPE_CHECKING:
    pass


class SpotifyConnection:
    # Spotify authentication URL for auth
    __auth_url = 'https://accounts.spotify.com/api/token'

    # Basic URL for API calls
    __base_url = 'https://api.spotify.com/v1/'

    # The time in seconds when the current token expires
    __token_expires = 0.0

    def __init__(self, clientID: str, clientSecret: str):
        """Create a Spotify Web API connection with client ID and client secret.

        Args:
            clientID (str): Client ID of the application
            clientSecret (str): Client Secret of the application

        Raises:
            Exception : When the connection is unsuccessful.
        """
        self.__clientID = clientID
        self.__clientSecret = clientSecret

    def __refresh_token(self):
        """Refreshes the access token if it's expired"""
        auth_response = requests.post(SpotifyConnection.__auth_url, {
            'grant_type': 'client_credentials',
            'client_id': self.__clientID,
            'client_secret': self.__clientSecret,
        }, verify=False)

        auth_response_data = auth_response.json()

        # If there is an error while connecting just raise it
        if 'error' in auth_response_data.keys():
            raise Exception(auth_response['error_description'])
        self.__access_token = auth_response_data['access_token']
        self.__token_expires = time.time() + auth_response_data['expires_in']


# Some test shit
connector = SpotifyConnection(
    'b2fbeaacf12d4b329a0e67000b92e356', '2e0555828d3f426a884f7bacb440e0d6')

try:
    connector.get_token()
except Exception as e:
    Logger.error(e)
