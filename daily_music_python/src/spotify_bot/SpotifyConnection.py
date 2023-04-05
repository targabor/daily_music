import requests
import time

from typing import TYPE_CHECKING
from src.python_logger.Logger import Logger
from src.helpers import string_helper


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
            return func(self, *args, **kwargs)
        return inner

    @check_token
    def __get_header(self) -> dict:
        """Returns auth header needed for web requests

        Returns:
            dict: Header with token
        """
        return_header = {'Authorization': f'Bearer {self.__access_token}'}
        return return_header

    @check_token
    def get_song_id_by_name(self, title: str, artist: str) -> str:
        """From a song title, returns it's song_id from Spotify API

        Args:
            title (str): Title of the song in str format
            artist (str): Artist of the song in str format

        Returns:
            str: Title's ID in Spotify
        """
        auth_header = self.__get_header()
        return_id = ''
        for i in range(4):
            if title == '':
                continue
            search_params = {
                'q': (f"{title} artist:{artist}" if artist != '' and i < 1 else title),
                'type': 'track',
                'limit': 1
            }

            search_url = self.__base_url + 'search'
            response = requests.get(
                search_url, headers=auth_header, params=search_params, verify=False)
            json_response = response.json()
            if json_response.get('error', '' != ''):
                raise Exception(
                    f"{json_response['error']} - {json_response['message']}")
            if json_response['tracks']['total'] == 0:
                return_id = 'NOT_FOUND'
                title, artist = artist, title
                continue

            if string_helper.compare_string(title, json_response['tracks']['items'][0]['name']):
                return_id = json_response['tracks']['items'][0]['id']
                break
            else:
                return_id = 'NOT FOUND'
                title, artist = artist, title

        return return_id
    

    @check_token
    def get_track_data(self, spotify_id: str):
        """get track data based on track_id from Spotify API

        Args:
            spotify_id (str): track_id of spotify song

        Returns:
            dict: spotify json response of track id
        """
        Logger.info('getting track data from spotify api....')
        auth_header = self.__get_header()
        track_url = self.__base_url + 'tracks/' + spotify_id
        response = requests.get(
            track_url, headers=auth_header, verify=False)
        json_response = response.json()
        return json_response

    @check_token
    def get_artist_genres(self, artist_id: str):
        """get genres linked to artist from Spotify API

        Args:
            spotify_id (str): track_id of spotify song

        Returns:
            dict: spotify json response of track id
        """
        Logger.info(f'Getting genres for artist with artis_id {artist_id} from spotify api')
        auth_header = self.__get_header()
        track_url = self.__base_url + 'artists/' + artist_id
        response = requests.get(
            track_url, headers=auth_header, verify=False)
        json_response = response.json()
        return json_response["genres"] if "genres" in json_response else []


connection = SpotifyConnection(
    'b2fbeaacf12d4b329a0e67000b92e356', 'ea1d1bada88b4f51b5ba7049628f4403')
