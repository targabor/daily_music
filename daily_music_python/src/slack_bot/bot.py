import slack
import os
import src.snowflake_functions.snowflake_functions as snowflake_functions
import re

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


def full_extraction():
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


full_extraction()
