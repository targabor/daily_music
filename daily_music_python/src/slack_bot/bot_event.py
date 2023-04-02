import slack
import os
import logging
import json

from flask import Flask, make_response, request
from slackeventsapi import SlackEventAdapter

SLACK_TOKEN = os.environ['SLACK_TOKEN']
SIGNING_SECRET = os.environ['SIGNING_SECRET']

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers


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


@app.route('/full_extraction', methods=['GET'])
def full_extraction():
    """It will load all music data from #daily_music Slack channel to snowflake"""
    channel_id = "C04UCUENRCG"
    return make_response('Done', 200)


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
