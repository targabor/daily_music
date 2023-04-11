import logging
import os
import time
import itertools
from src.helpers import spotify_helper
import traceback

from flask import Flask, make_response, request
from src.spotify_bot.SpotifyConnection import SpotifyConnection
from src.snowflake_functions import snowflake_functions

app = Flask(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

clientId = os.environ['clientId']
clientSecret = os.environ['clientSecret']

spotify_connection = SpotifyConnection(clientId, clientSecret)

TRACK_MODULE_NAME = 'track_processing'
ARTIST_MODULE_NAME = 'artist_processing'


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
            print(title_list[i])
        snowflake_functions.load_back_song_ids(title_list)
        return make_response(
            'Spotify IDs loaded successfully for non Spotify songs', 200)
    except Exception as e:
        return make_response(str(e), 500)


@app.route('/get_data_for_tracks', methods=['GET'])
def get_data_for_tracks():
    try:
        last_run_date = snowflake_functions.get_latest_extracted_ts(TRACK_MODULE_NAME)
        print(last_run_date)
        track_id_list =  snowflake_functions.get_new_track_ids(last_run_date)
        track_datas = []

        # get data fo tracks in batch
        slice_50 = slice(min(50, len(track_id_list)))
        track_batch = track_id_list[slice_50]
        del(track_id_list[slice_50])
        while len(track_batch) > 0:
            track_datas.extend(spotify_connection.get_several_tracks(track_batch))
            slice_50 = slice(min(50, len(track_id_list)))
            track_batch = track_id_list[slice_50]
            del(track_id_list[slice_50])
        # clean track data
        clean_track_datas = []
        for track in track_datas:
            clean_track_datas.extend(spotify_helper.clean_track_data(track))
        
        snowflake_functions.insert_spotify_data(clean_track_datas)
        snowflake_functions.log_module_run(TRACK_MODULE_NAME, 1)
        return make_response('inserted spotify_tracks', 200)
    except Exception as e:
        print(traceback.format_exc())
        snowflake_functions.log_module_run(TRACK_MODULE_NAME, 0)
        return(str(e), 500)



@app.route('/get_data_for_artists', methods=['GET'])
def get_data_for_artists():
    try:
        new_artist_ids = snowflake_functions.get_new_artist_ids()
        if len(new_artist_ids) == 0:
            return make_response(
            'no new artists to process', 200)
        new_artist_data = []
        # process artist data in batch and add it to a list
        slice_50 = slice(min(50, len(new_artist_ids)))
        artist_batch = new_artist_ids[slice_50]
        del(new_artist_ids[slice_50])
        while len(artist_batch) > 0:
            new_artist_data.extend(spotify_connection.get_artist_datas(artist_batch))
            slice_50 = slice(min(50, len(new_artist_ids)))
            artist_batch = new_artist_ids[slice_50]
            del(new_artist_ids[slice_50])
        
        snowflake_functions.insert_artists(new_artist_data)
        # checko for length
        insert_new_genres(new_artist_data)
        match_artist_genres(new_artist_data)
        snowflake_functions.log_module_run('artist_processing', 1)
        return make_response(
            'processed new artists', 200)
    except AttributeError as e:
        snowflake_functions.log_module_run('artist_processing', 0)
        return make_response(str(e), 500)
    

def insert_new_genres(new_artist_data):
    # get all genre names from db
    existing_genres = [genre[1] for genre in snowflake_functions.get_all_genres()]

    # check all new artists genre and insert into genre if not present
    genres_lst = [artist['genres'] for artist in new_artist_data]
    genres_set = set(itertools.chain.from_iterable(genres_lst))
    new_genres = [a for a in genres_set if a not in existing_genres]
    if len(new_genres) != 0:
        snowflake_functions.insert_genres(new_genres)


def match_artist_genres(new_artist_data):
    existing_genres = snowflake_functions.get_all_genres()
    existing_genres = {k: v for v, k in existing_genres}
    all_artist_genre_pairs = []
    for artist in new_artist_data:
        artist_genre = spotify_helper.make_genre_to_artist_pairs(artist['id'], artist['genres'], existing_genres)
        all_artist_genre_pairs.extend(artist_genre)
    snowflake_functions.insert_artist_genres(all_artist_genre_pairs)



if __name__ == "__main__":
    app.run(port= 5000, debug=True)
