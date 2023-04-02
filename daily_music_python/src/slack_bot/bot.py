import slack
import os

from src.python_logger.Logger import Logger
from datetime import datetime

SLACK_TOKEN = os.environ['SLACK_TOKEN']

client = slack.WebClient(token=SLACK_TOKEN)
# Store conversation history


def test():
    conversation_history = []
    # ID of the channel you want to send the message to
    channel_id = "C04UCUENRCG"
    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id)

        conversation_history = result["messages"]
        for message in conversation_history:
            print(message['ts'])
            dt_object = datetime.fromtimestamp(float(message['ts']))
            print(dt_object)
            if 'attachments' in message.keys():
                attachments = message['attachments']
                for attachment in attachments:
                    if attachment['service_name'] == 'YouTube':
                        print('Youtube', attachment['title'])
                    elif attachment['service_name'] == 'Spotify':
                        print('Spotify', attachment['from_url'])
            reaction_count = 0
            if 'reactions' in message.keys():
                reaction_count = sum([r['count']
                                      for r in message['reactions']])
            print(f'Reaction count : {reaction_count}')
    except Exception as e:
        Logger.error("Error creating conversation: {}".format(e))


def full_extraction():
    """It will load all music data from #daily_music Slack channel to snowflake"""
    channel_id = "C04UCUENRCG"
    result = client.conversations_history(channel=channel_id, limit=1000)
    print('first 1000')
    while result['has_more']:
        print()
        result = client.conversations_history(channel=channel_id,
                                              limit=1000,
                                              cursor=result['response_metadata']['next_cursor'])
        print('another 1000')


full_extraction()
