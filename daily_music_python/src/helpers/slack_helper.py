import re

from datetime import datetime


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
