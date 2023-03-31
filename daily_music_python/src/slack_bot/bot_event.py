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


@slack_event_adapter.on('message')
def message(payload):
    app.logger.warning(payload)


@app.route('/slack_challenge', methods=["POST"])
def hello_slack():
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
    response = make_response('OK', 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


@ slack_event_adapter.on('message')
def message(payload):
    gunicorn_logger.warning(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if text == "hi":
        client.chat_postMessage(channel=channel_id, text="Hello")


if __name__ == "__main__":
    app.run(debug=True)
