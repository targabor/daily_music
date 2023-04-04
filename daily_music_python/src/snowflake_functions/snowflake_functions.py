import snowflake.connector
from src.snowflake_functions.SnowflakeCredentials import SnowflakeCredentials
from datetime import datetime


def __connect_to_snowflake(credentials: SnowflakeCredentials) -> snowflake.connector.SnowflakeConnection:
    """Creates snowflake connection

    Args:
        user (str): Snowflake username inside account
        password (str): Password for account
        account (str): Snowflake account without ".snowflakecomputing.com"
        warehouse (str): Warehouse name
        database (str): Database name
        schema (str): Schema name

    Returns:
        snowflake.connector.SnowflakeConnection: Instance of connection to Snowflake
    """
    conn = snowflake.connector.connect(
        user=credentials.user,
        password=credentials.password,
        account=credentials.account,
        warehouse=credentials.warehouse,
        database=credentials.database,
        schema=credentials.schema,
    )
    return conn


def load_raw_messages_into_snowflake(messages):
    """It loads raw Slack responds into Snowflake

    Args:
        messages (slack.app.conversation_history response): Filtered Slack response messages
    """
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('EXTRACTED')) as connection:
        insert_query = '''INSERT INTO EXTRACTED_MESSAGES (CLIENT_MSG_ID,SLACK_ID,MESSAGE_TIME,SERVICE_NAME,ORIGINAL_URL,ARTIST,TITLE,SPOTIFY_ID,REACTION_COUNT,PROCESSING_STATUS)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'')'''
        connection.cursor().executemany(insert_query, messages)
        connection.commit()


def get_latest_extracted_ts() -> str:
    """
    Returns the TimeStamp of the latest extracted message

    Returns:
        str: latest message TimeStamp
    """
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('META')) as connection:
        select_query = '''SELECT TOP 1 run_datetime
                            FROM etl_run_log
                            WHERE status = 1
                            ORDER BY run_datetime DESC;'''
        row = connection.cursor().execute(select_query).fetchone()
        return datetime.timestamp(row[0]) if row is not None else 0


def get_new_youtube_songs() -> list[dict]:
    """This function returns all of that newly extracted songs, that came from YouTube.

    Returns:
        list[dict]: List of songs
    """
    title_list = []
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('EXTRACTED')) as connection:
        select_query = """SELECT ID, ARTIST, TITLE
                            FROM EXTRACTED_MESSAGES
                            WHERE PROCESSING_STATUS = '' AND SERVICE_NAME != 'Spotify';"""
        cursor = connection.cursor()
        for row in cursor.execute(select_query).fetchall():
            title_list.append({'id': row[0],
                               'artist': row[1],
                               'title': row[2],
                               'spotify_id': ''})
        cursor.close()
        return title_list


def load_back_song_ids(title_list):
    """It loads back spotify IDs for non Spotify songs

    Args:
        title_list (list with dicts): Title list (came from get_new_youtube_songs)
    """
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('EXTRACTED')) as connection:
        update_query = f""" UPDATE EXTRACTED_MESSAGES
                            SET SPOTIFY_ID = %s,
                                PROCESSING_STATUS = 'SPOTIFY_ID'
                            WHERE ID = %s; """
        cursor = connection.cursor()
        cursor.executemany(update_query,
                           [(d['spotify_id'], d['id']) for d in title_list])
        connection.commit()
        cursor.close()


def get_new_track_ids(from_date: str):
    # todo filter out existing data
    """ 
        Returns:
            all spotify id's sent in after a specific date

        Args:
            from_date: query spotify_ids sent after this date
    """
    print('from_date:', from_date)
    from_date = datetime.fromtimestamp(from_date)
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('EXTRACTED')) as connection:
        query = f""" SELECT SPOTIFY_ID
                    FROM EXTRACTED_MESSAGES
                    WHERE MESSAGE_TIME >= %s AND SPOTIFY_ID != 'NOT FOUND'
                """
        cursor = connection.cursor()
        track_ids = cursor.execute(query, (from_date,)).fetchall()
        cursor.close()
        return [track_id[0] for track_id in track_ids]


def log_module_run(module_name: str, status: int):
    """ Insert current datetime into etl_run_log table

        Args:
            module_name: etl module
            status: 1 if successfull, 0 if not
    """
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('META')) as connection:
        query = f""" INSERT INTO daily_music.meta.etl_run_log (module, status, run_datetime)
                    VALUES (
                    %s, %s, %s
                    )
                """
        cursor = connection.cursor()
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query, (module_name, status, formatted_date))
        cursor.close()


def insert_spotify_data(track_list: list):
    """Insert Spotify data into CONSOLIDATED.spotify_track

    Args:
        track_list: list of tracks in dict format
    """
    with __connect_to_snowflake(SnowflakeCredentials.get_credentialsFor('CONSOLIDATED')) as connection:
        update_query = f""" INSERT INTO spotify_track (track_id, artist_id, title, popularity)
                            VALUES %s, %s, %s, %s
                        """
        cursor = connection.cursor()
        cursor.executemany(update_query,
                           [(track['spotify_id'],
                             track['artist_id'],
                             track['title'],
                             track['popularity']) for track in track_list])
        connection.commit()
        cursor.close()


            