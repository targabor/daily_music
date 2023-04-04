import logging
import os
import time

from src.helpers import spotify_helper

from flask import Flask, make_response, request
from src.spotify_bot.SpotifyConnection import SpotifyConnection
from src.snowflake_functions import snowflake_functions

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

clientId = os.environ['clientId']
clientSecret = os.environ['clientSecret']

spotify_connection = SpotifyConnection(clientId, clientSecret)


@app.route('/status', methods=['GET'])
def status():
    """Basic status check for spotify_app status"""
    response = make_response('Spotify App Status: OK', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/get_id_for_youtube_songs', methods=['GET'])
def get_id_for_youtube_songs():
    """It will load the spotify_id for the songs that came from YouTube, if there is no result, it'll set the status "Not Found" """
    try:
        title_list = snowflake_functions.get_new_youtube_songs()
        for i in range(len(title_list)):
            print(i)
            # Check the title column from the extracted table
            song_id = spotify_connection.get_song_id_by_name(
                title_list[i]['title'], title_list[i]['artist'])
            time.sleep(0.3)
            title_list[i]['spotify_id'] = song_id
        snowflake_functions.load_back_song_ids(title_list)
        return make_response(
            'Spotify IDs loaded successfully for non Spotify songs', 200)
    except Exception as e:
        return make_response(str(e), 500)


@app.route('/get_data_for_tracks', methods=['GET'])
def get_genres_for_songs():
    try:
        last_run_date = snowflake_functions.get_latest_extracted_ts()
        print(last_run_date)
        # todo filter if track already present
        track_id_list =  snowflake_functions.get_track_ids(last_run_date)
        track_datas = []
        for track_id in track_id_list:
            print('track_id: ', track_id, type(track_id))
            spotify_track_data = spotify_connection.get_track_data(track_id)
            track_datas.extend(spotify_helper.clean_track_data(spotify_track_data))
            for artist in spotify_track_data.get("artists"):
                if "genres" in artist:
                    print(artist.get("genres"))
                    # check if we can get genres
        return make_response(
            'get genres function run without errors', 200)
    except AttributeError as e:
        return make_response(str(e), 500)
    


if __name__ == "__main__":
    app.run(debug=True)
