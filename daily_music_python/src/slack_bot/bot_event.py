import slack
import os
import logging
import json
import re
import subprocess
import traceback

from flask import Flask, make_response, request
from slackeventsapi import SlackEventAdapter
from src.snowflake_functions import snowflake_functions
from src.helpers import slack_helper
from datetime import datetime

SLACK_TOKEN = os.environ['SLACK_TOKEN']
# SIGNING_SECRET = os.environ['SIGNING_SECRET']

app = Flask(__name__)
# slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers

SLACK_MODULE_NAME = 'slack_processing'


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
    try:
        latest_ts = snowflake_functions.get_latest_extraction_ts()
        channel_id = "C04UCUENRCG"
        result = client.conversations_history(
            channel=channel_id, limit=100, oldest=str(latest_ts))
        filtered_messages = slack_helper.filter_songs_out(result['messages'])
        snowflake_functions.load_raw_messages_into_snowflake(filtered_messages)
        while result['has_more']:
            result = client.conversations_history(channel=channel_id,
                                                  limit=100,
                                                  cursor=result['response_metadata']['next_cursor'])
            filtered_messages = slack_helper.filter_songs_out(
                result['messages'])
            snowflake_functions.load_raw_messages_into_snowflake(
                filtered_messages)
        snowflake_functions.log_module_run(SLACK_MODULE_NAME, 1)
        return make_response('Extraction is done', 200)
    except Exception as e:
        snowflake_functions.log_module_run(SLACK_MODULE_NAME, 0)
        traceback.print_exc()
        return make_response(str(e), 500)


@app.route('/dummy_extract', methods=['GET'])
def dummy_extract():
    """It will load all music data from #daily_music Slack channel to snowflake"""
    try:
        channel_id = "C04UCUENRCG"
        result = client.conversations_history(
            channel=channel_id, limit=1000)
        for message in result['messages']:
            for attachment in message['attachments']:
                song_data = []
                if attachment['original_url'].startswith('https://spotify.link'):
                    output = subprocess.check_output(
                        ['curl', attachment['original_url'], '-I', '--ssl-no-revoke'])
                    headers = output.decode('utf-8').splitlines()
                    for header in headers:
                        if header.startswith('Location:'):
                            print(header.split(' ')[1])

        return make_response(output, 200)
    except Exception as e:
        return make_response(str(e), 500)


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
    app.run(port=5001, debug=True)
