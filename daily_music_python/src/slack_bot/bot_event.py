import slack
import os
import logging
import json
import re

from flask import Flask, make_response, request
from slackeventsapi import SlackEventAdapter
from src.snowflake_functions import snowflake_functions
from datetime import datetime

SLACK_TOKEN = os.environ['SLACK_TOKEN']
# SIGNING_SECRET = os.environ['SIGNING_SECRET']

app = Flask(__name__)
# slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers


def clear_title(title: str) -> tuple[str, str]:
    """It clears the unnecessary symbols from song titles and returns the artist and song name (only for YouTube songs).

    Args:
        title (str): Title of song

    Returns:
        tuple[str, str]: The first string is the artist and the second is the title of the song.
    """
    title_regex = re.compile(
        r'^(?P<artist>.+?)\s*[:\-]\s*(?P<song>.+?)(\s*\(.+?\))*$')
    match = title_regex.match(title)

    if match:
        artist = match.group('artist')
        song_name = match.group('song')
        return (artist, song_name)
    else:
        return ('', title)


def get_spotify_id(spotify_url: str) -> str:
    """From the url it returns the song's ID

    Args:
        spotify_url (str): _description_

    Returns:
        str: _description_
    """
    id_regex = re.compile(
        r'https://(?:open\.spotify\.com/track|spotify\.link)/(?P<song_id>\w+)')
    match = id_regex.match(spotify_url)

    if match:
        return match.group('song_id')
    else:
        return ''


def filter_songs_out(messages):
    """It filters out that type of messages what we wont upload into snowflake.

    Args:
        messages: Response from Slack API 
    """
    # Prepare the format of data to store it easier
    filtered_data = []
    for message in messages:
        if message.get('subtype', '') == 'channel_join' or message.get('subtype', '') == 'channel_left':
            # Channel joins or leaves
            continue
        if message.get('attachments', '') == '':
            # Mostly simple messages
            continue
        # If there is an attachment, there is a song
        for attachment in message['attachments']:
            song_data = []
            song_data.append(message.get('client_msg_id', None))
            song_data.append(message['user'])
            song_data.append(datetime.fromtimestamp(
                float(message.get('ts', 0.0))).strftime('%Y-%m-%d %H:%M:%S.%f'))
            song_data.append(attachment['service_name'])
            song_data.append(attachment['original_url'])
            song_data.extend(clear_title(attachment['title']))
            song_data.append(get_spotify_id(attachment['original_url']))
            song_data.append(sum([r.get('count', 0)
                             for r in message.get('reactions', [])]))
            filtered_data.append(song_data)
    return filtered_data


@app.route('/slack_challenge', methods=["POST"])
def hello_slack():
    """This method needed to connect Slack's event driven API"""
    try:
        app.logger.warning(request.get_json(silent=True, force=True))
        request_json = request.get_json(silent=True, force=True)
        if request_json.get("challenge") is not None:
            response = make_response(request_json.get("challenge"), 200)
            response.headers['Content-Type'] = 'text/plain'
            return response
        return make_response('This endpoint is reserved for Slack\'s verification.', 400)
    except Exception as e:
        app.logger.warning(e)
        return make_response(str(e), 500)


@app.route('/status', methods=['GET'])
def status():
    """Basic status check for Slack API"""
    response = make_response('Slack App Status: OK', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/extract_data', methods=['GET'])
def extract_data():
    """It will load all music data from #daily_music Slack channel to snowflake"""
    channel_id = "C04UCUENRCG"
    result = client.conversations_history(channel=channel_id, limit=100)
    filtered_messages = filter_songs_out(result['messages'])
    snowflake_functions.load_raw_messages_into_snowflake(filtered_messages)
    while result['has_more']:
        result = client.conversations_history(channel=channel_id,
                                              limit=100,
                                              cursor=result['response_metadata']['next_cursor'])
        filtered_messages = filter_songs_out(result['messages'])
        snowflake_functions.load_raw_messages_into_snowflake(filtered_messages)


# Currently it's buggy (every event triggers twice)
# @slack_event_adapter.on('message')
# def message(payload):
#     gunicorn_logger.warning(payload)
#     event = payload.get('event', {})
#     channel_id = event.get('channel')
#     user_id = event.get('user')
#     text = event.get('text')
#     gunicorn_logger.warning(
#         f'channel:{channel_id} \t user:{user_id} \t text:{text}')
#     if text == "hi":
#         client.chat_postMessage(channel=channel_id, text="Hello")

if __name__ == "__main__":
    app.run(debug=True)
