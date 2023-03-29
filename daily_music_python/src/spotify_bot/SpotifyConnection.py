import requests

from typing import TYPE_CHECKING
from src.python_logger.Logger import Logger
# Place there the imports which are needed only for type checking
if TYPE_CHECKING:
    pass


class SpotifyConnection:
    # Spotify authentication URL for APIs
    __auth_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, clientID: str, clientSecret: str):
        """Create a Spotify Web API connection with client ID and client secret.

        Args:
            clientID (str): Client ID of the application
            clientSecret (str): Client Secret of the application
        """
        self.__clientID = clientID
        self.__clientSecret = clientSecret

    def connect(self):
        """Connects to the web API with the given ID and secret"""
        auth_response = requests.post(SpotifyConnection.__auth_url, {
            'grant_type': 'client_credentials',
            'client_id': self.__clientID,
            'client_secret': self.__clientSecret,
        }, verify=False)

        auth_response_data = auth_response.json()

        # If there is an error while connecting just raise it
        if auth_response.has_key('error'):
            raise Exception(auth_response['error_description'])
        print(auth_response)
        self.__auth_token = None


connector = SpotifyConnection(
    'b2fbeaacf12d4b329a0e67000b92e356', '2e0555828d3f426a884f7bacb440e0d6')

try:
    connector.connect()
except Exception as e:
    Logger.error(e)
