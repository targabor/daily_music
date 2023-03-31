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


@slack_event_adapter.on('challenge')
def challenge(challenge):
    request_json = request.get_json(silent=True, force=True)
    response_body = json.dumps(request_json)
    response = make_response((), 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


if __name__ == "__main__":
    app.run(debug=True)
