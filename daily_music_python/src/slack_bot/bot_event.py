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


@app.route('/slack_challenge')
def hello_slack():
    request_json = request.get_json(silent=True, force=True)
    if request_json.get("challenge") is not None:
        return make_response(request_json.get("challenge"), 200, "text/plain")


if __name__ == "__main__":
    app.run(debug=True)
