import slack
import os

from flask import Flask
from slackeventsapi import SlackEventAdapter

SLACK_TOKEN = os.environ['SLACK_TOKEN']
SIGNING_SECRET = os.environ['SIGNING_SECRET']

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(SIGNING_SECRET, '/slack/events', app)

client = slack.WebClient(token=SLACK_TOKEN)
client.chat_postMessage(channel='#bot-test', text='Hello World!')


@ slack_event_adapter.on('message')
def message(payload):
    print(payload)


if __name__ == "__main__":
    app.run(debug=True)
