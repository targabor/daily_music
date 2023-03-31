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
            return make_response(request_json.get("challenge"), 200, "text/plain")
        return make_response('This endpoint is reserved for Slack\'s verification.', 400, "text/plain")
    except Exception as e:
        app.logger.warning(e)
        return make_response(str(e), 500, "text/plain")


@app.route('status', methods=['GET'])
def status():
    return make_response('OK', 200, "text/plain")


if __name__ == "__main__":
    app.run(debug=True)
