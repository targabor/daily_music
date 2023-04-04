import logging
import os
import time

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
        make_response(
            'Spotify IDs loaded successfully for non Spotify songs', 200)
    except Exception as e:
        make_response(str(e), 500)


@app.route('/get_data_for_tracks', methods=['GET'])
def get_genres_for_songs():
    try:
        snowflake_functions.log_module_run('test', 1)
        # last_run_date = snowflake_functions.get_latest_extracted_ts().strftime("%Y-%m-%d %H:%M:%S")
        last_run_date = '2020-01-01 00:00:00'
        track_id_list =  snowflake_functions.get_track_ids(last_run_date)
        # check if len > 50, if not, it can go out in one request
        if len(track_id_list) <= 50:
            # make api call to spotify
            track_datas = spotify_connection.get_tracks()
            # from here get artist info
            # go through atrists and get the relevant genre, popularity
        return make_response(
            'get genres function run without errors', 200)
    except AttributeError as e:
        return make_response(str(e), 500)
    


if __name__ == "__main__":
    app.run(debug=True)
