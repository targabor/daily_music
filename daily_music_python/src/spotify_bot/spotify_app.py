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
        track_id_list =  snowflake_functions.get_new_track_ids(last_run_date)
        track_datas = []

        for track_id in track_id_list:
            print('track_id: ', track_id, type(track_id))

            # get track data from spotify and convert it to a format to ease insertion into snowflake
            spotify_track_data = spotify_connection.get_track_data(track_id)
            #print("spotify_track_data: " + str(spotify_track_data))
            track_data = spotify_helper.clean_track_data(spotify_track_data)
            print(track_data)
            track_datas.extend(track_data)
            
            new_artist_ids = spotify_helper.get_new_artists(snowflake_functions.get_all_artists(), set([track["artist_id"] for track in track_data]))
            
            # initialize list to append artis - genre name information to
            artists_genres = []

            existing_genres = [genre[1] for genre in snowflake_functions.get_all_genres()]
            for new_artist_id in new_artist_ids:

                genres = spotify_connection.get_artist_genres(new_artist_id)
                new_genres = spotify_helper.get_new_genres(existing_genres, genres)
                print(f'\n\n------{new_genres}')
                # insert new genres into snowflake
                if len(new_genres) != 0:
                    snowflake_functions.insert_genres(new_genres)
                    existing_genres.extend(new_genres)
                
                artist_genres = spotify_helper.make_genre_to_artist_pairs(new_artist_id, genres)
                artists_genres.extend(artist_genres)
            print(f"artist-genrename {artists_genres}")
            all_genres = spotify_helper.tuple_pairs_to_dict(snowflake_functions.get_all_genres())
        
            artists_genres = [(artist, all_genres[genre]) for artist, genre in artists_genres]
            print(artist_genres)
            snowflake_functions.insert_artist_genres(artists_genres)
        snowflake_functions.insert_spotify_data(track_datas)
        return make_response(
            'get genres function run without errors', 200)
    except AttributeError as e:
        return make_response(str(e), 500)
    


if __name__ == "__main__":
    app.run(debug=True)
