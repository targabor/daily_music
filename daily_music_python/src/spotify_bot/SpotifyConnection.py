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

    # Wrapper function that makes easier to manage access tokens
    def check_token(func):
        # It checks every time before any method call inside a class
        # that the token is still active
        def inner(self, *args, **kwargs):
            if self.__token_expires <= time.time():
                print('Getting new token')
                self.__refresh_token()
            func(self, *args, **kwargs)
        return inner
